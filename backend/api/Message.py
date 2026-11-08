import sqlite3
from fastapi import APIRouter, HTTPException
from schemas.Message import RequestMessage, ConversationInconnue
from contextlib import closing
from services.assistant import ask_medimind, ModeleIndisponible
from fastapi.responses import JSONResponse
from db.database import get_connection

router = APIRouter()

# function to verify if conversation exist by id
def verifyConversationById(conn, id_conversation: int):
    row = conn.execute(
        "SELECT * FROM conversation "
        "WHERE id = ?",
        (id_conversation,)
    ).fetchone() 

    if row is None:
        raise ConversationInconnue()

# function to findAll message by conversation
def findByConversation(id_conversation: int):
    with closing(get_connection()) as conn, conn:

        verifyConversationById(conn, id_conversation)

        rows = conn.execute(
            "SELECT * "
            "FROM message WHERE id_conversation = ? ORDER BY id",
            (id_conversation,)
        ).fetchall()

        return [dict(row) for row in rows]

# function to create conversation with message
def create_conversation_message(role: str, content: str):
    with closing(get_connection()) as conn, conn:
        cur = conn.execute(
            "INSERT INTO conversation (first_message) VALUES (?)",
            (content,)
        )
        id_conversation = cur.lastrowid

        cur = conn.execute(
            "INSERT INTO message (role, content, id_conversation) VALUES (?, ?, ?)",
            (role, content, id_conversation)
        )
        id_message = cur.lastrowid

    return id_conversation, id_message

# function to insert message
def create_message(role: str, content: str, id_conversation: int):
    with closing(get_connection()) as conn, conn:

        verifyConversationById(conn, id_conversation)

        cur = conn.execute(
            "INSERT INTO message (role, content, id_conversation) VALUES (?, ?, ?)",
            (role, content, id_conversation)
        )
        return cur.lastrowid

# route to findAll message
@router.get("/api/message")
def messages(id_conversation: int):

    messages = findByConversation(id_conversation)

    return JSONResponse(
        status_code = 200,
        content = {
            "data": messages
        }
    )
    

# route to create new conversation 
@router.post("/api/message")
def send_message(data: RequestMessage):
    # create new message with conversation
    if data.id_conversation is None:
        id_conversation, id_message = create_conversation_message('user', data.message)

        return JSONResponse(
            status_code = 200,
            content = {
                "id_message": id_message,
                "id_conversation": id_conversation,
                "role": "user",
                "content": data.message
            }
        )

    else:
        id_message = create_message('user', data.message, data.id_conversation)

        return JSONResponse(
            status_code = 200,
            content = {
                "id_message": id_message,
                "id_conversation": data.id_conversation,
                "role": "user",
                "content": data.message
            }
        )

# route to send message and get response
@router.post("/api/message/traitement")
def traitement_message(data: RequestMessage):
    if data.id_conversation is None:
        raise HTTPException(status_code=422, detail="L'identifiant de conversation est requis.")

    # Vérification AVANT l'appel au LLM : on ne paie pas une réponse pour rien
    with closing(get_connection()) as conn:
        verifyConversationById(conn, data.id_conversation)

    # try except for asking medimind
    try:
        resultat = ask_medimind(data.message, [m.model_dump()  for m in data.historique], data.langue)
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
    id_message = create_message('assistant', resultat["reponse"], data.id_conversation)

    return JSONResponse(
        status_code = 200,
        content = {
            "id_message": id_message,
            "role": "assistant",
            "content": resultat["reponse"],
            "id_conversation": data.id_conversation,
            "alerte": resultat["alerte"],
            "orienter": resultat["orienter"],
        }
    )