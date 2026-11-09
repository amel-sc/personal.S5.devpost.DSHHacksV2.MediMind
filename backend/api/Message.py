import sqlite3
from fastapi import APIRouter, Depends, HTTPException
from schemas.Message import RequestMessage, ConversationInconnue
from contextlib import closing
from services.assistant import ask_medimind, ModeleIndisponible
from fastapi.responses import JSONResponse
from db.database import get_connection
from api.Auth import utilisateur_connecte
from api.HumeurJours import findByDateJour

router = APIRouter()

# À adapter aux valeurs réelles de ta table humeur.
# Exemple uniquement si 1 = très bien ... 5 = très mal.
LIBELLES_HUMEUR = {
    1: "très bien",
    2: "bien",
    3: "moyen",
    4: "mal",
    5: "très mal",
}

# À adapter aux codes réels de ta table humeur_cause.
LIBELLES_CAUSES = {
    "sommeil":"sommeil",
    "stress":"stress",
    "famille":"famille",
    "etudes":"etudes",
    "amis":"amis",
    "sante":"sante",
    "couple":"couple",
    "autre":"autre",
}

def construire_contexte_humeur(humeur, causes):
    if humeur is None:
        return None

    # On n'utilise pas directement une description issue de la base
    # comme instruction destinée au modèle.
    try:
        valeur = int(humeur["humeur_val"])
    except (TypeError, ValueError, KeyError):
        return None

    libelle = LIBELLES_HUMEUR.get(valeur)
    if libelle is None:
        return None

    codes_causes = [
        cause["code"]
        for cause in causes
        if cause.get("code") in LIBELLES_CAUSES
    ]

    return {
        "humeur": libelle,
        "causes": [LIBELLES_CAUSES[code] for code in codes_causes],
    }

# function to get last twelve conversation by id
def find12LastMessageByConversation(id_conversation: int, id_user: int):
    with closing(get_connection()) as conn:
        verifyConversationById(conn, id_conversation, id_user)

        # On récupère les 12 plus récents...
        rows = conn.execute(
            "SELECT id, role, content "
            "FROM message "
            "WHERE id_conversation = ? "
            "ORDER BY id DESC "
            "LIMIT 12",
            (id_conversation,),
        ).fetchall()

    # ...puis on les transmet au modèle du plus ancien au plus récent.
    return [dict(row) for row in reversed(rows)]

# function to verify if conversation exist by id
def verifyConversationById(conn, id_conversation: int, id_user: int):
    row = conn.execute(
        "SELECT * FROM conversation "
        "WHERE id = ? AND id_user = ?",
        (id_conversation, id_user)
    ).fetchone() 

    if row is None:
        raise ConversationInconnue()

# function to findAll message by conversation
def findByConversation(id_conversation: int, id_user: int):
    with closing(get_connection()) as conn, conn:

        verifyConversationById(conn, id_conversation, id_user)

        rows = conn.execute(
            "SELECT * "
            "FROM message WHERE id_conversation = ? ORDER BY id",
            (id_conversation,)
        ).fetchall()

        return [dict(row) for row in rows]

# function to create conversation with message
def create_conversation_message(role: str, content: str, id_user: int):
    with closing(get_connection()) as conn, conn:
        cur = conn.execute(
            "INSERT INTO conversation (first_message, id_user) VALUES (?, ?)",
            (content, id_user)
        )
        id_conversation = cur.lastrowid

        cur = conn.execute(
            "INSERT INTO message (role, content, id_conversation) VALUES (?, ?, ?)",
            (role, content, id_conversation)
        )
        id_message = cur.lastrowid

    return id_conversation, id_message

# function to insert message
def create_message(role: str, content: str, id_conversation: int, alerte: int, id_user: int):
    with closing(get_connection()) as conn, conn:

        verifyConversationById(conn, id_conversation, id_user)

        cur = conn.execute(
            "INSERT INTO message (role, content, id_conversation, alerte) VALUES (?, ?, ?, ?)",
            (role, content, id_conversation, alerte)
        )
        return cur.lastrowid

# route to findAll message
@router.get("/api/message")
def messages(id_conversation: int, utilisateur: dict = Depends(utilisateur_connecte)):

    messages = findByConversation(id_conversation, utilisateur["id"])

    return JSONResponse(
        status_code = 200,
        content = {
            "data": messages
        }
    )
    

# route to create new conversation 
@router.post("/api/message")
def send_message(data: RequestMessage, utilisateur: dict = Depends(utilisateur_connecte)):

    id_user = utilisateur["id"]
    # create new message with conversation
    if data.id_conversation is None:
        id_conversation, id_message = create_conversation_message('user', data.message, id_user)

        return JSONResponse(
            status_code = 200,
            content = {
                "id_message": id_message,
                "id_conversation": id_conversation,
                "role": "user",
                "content": data.message,
                "alerte": 0
            }
        )

    else:
        id_message = create_message('user', data.message, data.id_conversation, 0, id_user)

        return JSONResponse(
            status_code = 200,
            content = {
                "id_message": id_message,
                "id_conversation": data.id_conversation,
                "role": "user",
                "content": data.message,
                "alerte": 0
            }
        )

# route to send message and get response
@router.post("/api/message/traitement")
def traitement_message(data: RequestMessage, utilisateur: dict = Depends(utilisateur_connecte)):
    if data.id_conversation is None:
        raise HTTPException(status_code=422, detail="L'identifiant de conversation est requis.")

    id_user = utilisateur["id"]

    # Vérification AVANT l'appel au LLM : on ne paie pas une réponse pour rien
    with closing(get_connection()) as conn:
        verifyConversationById(conn, data.id_conversation, id_user)

    # try except for asking medimind
    try:
        # get conversation in base for historique
        historique = find12LastMessageByConversation(data.id_conversation, id_user)

        # Le message actuel est déjà enregistré par /api/message.
        # On le retire de l'historique puisqu'ask_medimind l'ajoutera lui-même.
        if (
            historique
            and historique[-1]["role"] == "user"
            and historique[-1]["content"] == data.message
        ):
            historique.pop()

        # find humeur actuel
        humeur_actuelle, causes_actuelles = findByDateJour(id_user)
        contexte_humeur = construire_contexte_humeur(
            humeur_actuelle,
            causes_actuelles,
        )

        resultat = ask_medimind(
            data.message,
            historique,
            data.langue,
            contexte_humeur=contexte_humeur,
        )
    except ModeleIndisponible:
        return JSONResponse(
            status_code=503,
            content={
                "code": "modele_indisponible",
                "message": "Modèle indisponible.", 
                "errors": {}
            },
        )
    # insert response in base
    alerte = 1 if resultat["alerte"] is not None else 0
    id_message = create_message('assistant', resultat["reponse"], data.id_conversation, alerte, id_user)

    return JSONResponse(
        status_code = 200,
        content = {
            "id_message": id_message,
            "role": "assistant",
            "content": resultat["reponse"],
            "id_conversation": data.id_conversation,
            "alerte": alerte,
            "orienter": resultat["orienter"],
        }
    )