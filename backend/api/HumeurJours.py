import sqlite3
from fastapi import APIRouter, Path, Depends
from schemas.HumeurJours import HumeurJours, HumeurInconnue, CauseInconnue
from contextlib import closing
from services.assistant import ask_medimind
from fastapi.responses import JSONResponse
from db.database import get_connection
from datetime import datetime, timedelta, timezone
from api.Auth import utilisateur_connecte

router = APIRouter()

# function to find humeur actif du jour (humeur_jours_status.val = 1, date_creation = now)
def findByDateJour(id_user: int):
    date_jour = datetime.now(timezone.utc).date()
    date_jour_plus1 = date_jour + timedelta(days=1)

    with closing(get_connection()) as conn, conn:
        row = conn.execute(
            "SELECT hj.id, hj.note, hj.date_creation, hj.id_humeur AS humeur_id, hj.id_humeur_jours_status AS status_id, "
            "       h.val   AS humeur_val, "
            "       h.desce AS humeur_desce, "
            "       hjs.val AS status_val, "
            "       hjs.desce AS status_desce "
            "FROM humeur_jours hj "
            "LEFT JOIN humeur h ON h.id = hj.id_humeur "
            "LEFT JOIN humeur_jours_status hjs ON hjs.id = hj.id_humeur_jours_status "
            "WHERE (hj.date_creation >= ? AND hj.date_creation < ?) "
            "AND hj.id_humeur_jours_status = (SELECT id FROM humeur_jours_status WHERE val = 1) "
            "AND hj.id_user = ?"
            "LIMIT 1",
            (date_jour, date_jour_plus1, id_user)
        ).fetchone()

        if row is not None:
            temp = dict(row)
            row_causes = conn.execute(
                "SELECT hjc.id AS id, hc.id AS id_cause, hc.val AS cause_val, hc.desce AS cause_desce, hc.code "
                "FROM humeur_jours_causes hjc "
                "LEFT JOIN humeur_cause hc ON hc.id = hjc.id_humeur_cause "
                "WHERE id_humeur_jours = ?",
                (temp['id'],)
            ).fetchall()

    if row is None:          
        return (None, None)
    return (dict(row), None if row_causes is None else [dict(row_cause) for row_cause in row_causes])

# function to find humeur_jours by id
def findById(id: int, id_user: int):
    with closing(get_connection()) as conn:  # lecture seule : pas besoin de transaction
        row = conn.execute(
            "SELECT hj.id, hj.note, hj.date_creation, "
            "       h.val     AS humeur_val, "
            "       h.desce   AS humeur_desce, "
            "       hjs.val   AS status_val, "
            "       hjs.desce AS status_desce "
            "FROM humeur_jours hj "
            "LEFT JOIN humeur h ON h.id = hj.id_humeur "
            "LEFT JOIN humeur_jours_status hjs ON hjs.id = hj.id_humeur_jours_status "
            "WHERE hj.id = ? AND hj.id_user = ?",
            (id, id_user)
        ).fetchone()

        if row is None:
            return (None, [])

        row_causes = conn.execute(
            "SELECT hjc.id AS id, hc.id AS id_cause, hc.val AS cause_val, hc.desce AS cause_desce, hc.code "
            "FROM humeur_jours_causes hjc "
            "LEFT JOIN humeur_cause hc ON hc.id = hjc.id_humeur_cause "
            "WHERE hjc.id_humeur_jours = ? "
            "ORDER BY hc.id",
            (id,)
        ).fetchall()

    return (dict(row), [dict(r) for r in row_causes])

# function to insert new humeur jours
def create(val_humeur: int, note: str, humeur_causes: list[int], id_user: int):
    date_jour = datetime.now(timezone.utc).date()
    date_jour_plus1 = date_jour + timedelta(days=1)

    with closing(get_connection()) as conn, conn:
        row = conn.execute("SELECT id FROM humeur WHERE val = ?", (val_humeur,)).fetchone()
        if row is None:
            raise HumeurInconnue(val_humeur)
        id_humeur = row["id"]

        # vérifier l'existence de la cause de l'humeur
        if humeur_causes:
            # Le f-string ne contient que des "?" : les valeurs restent paramétrées (pas d'injection SQL)
            marqueurs = ",".join("?" * len(humeur_causes))
            nb = conn.execute(
                f"SELECT COUNT(*) FROM humeur_cause WHERE id IN ({marqueurs})",
                humeur_causes,
            ).fetchone()[0]
            if nb != len(humeur_causes):
                raise CauseInconnue()

        # 1. L'humeur active du jour passe en "Autre" (val = 2)
        conn.execute(
            "UPDATE humeur_jours "
            "SET id_humeur_jours_status = (SELECT id FROM humeur_jours_status WHERE val = 2) "
            "WHERE id_humeur_jours_status = (SELECT id FROM humeur_jours_status WHERE val = 1) "
            "AND id_user = ? "
            "AND date_creation >= ? AND date_creation < ?",
            (id_user, date_jour, date_jour_plus1),
        )

        # 2. Insertion de la nouvelle humeur active
        cur = conn.execute(
            "INSERT INTO humeur_jours (id_humeur, note, id_humeur_jours_status, id_user) "
            "VALUES (?, ?, (SELECT id FROM humeur_jours_status WHERE val = 1), ?)",
            (id_humeur, note, id_user),
        )
        id_humeur_jours = cur.lastrowid

        # 3. Causes (set() retire les doublons)
        conn.executemany(
            "INSERT INTO humeur_jours_causes (id_humeur_jours, id_humeur_cause) VALUES (?, ?)",
            [(id_humeur_jours, c) for c in set(humeur_causes)],
        )

    return id_humeur_jours

# function to findAll humeur jours 
def findAll(id_user: int):
    with closing(get_connection()) as conn:
        rows = conn.execute(
            "SELECT hj.id, hj.note, hj.date_creation, hj.id_humeur AS humeur_id, hj.id_humeur_jours_status AS status_id, "
            "       h.val   AS humeur_val, "
            "       h.desce AS humeur_desce, "
            "       hjs.val AS status_val, "
            "       hjs.desce AS status_desce "
            "FROM humeur_jours hj "
            "LEFT JOIN humeur h ON h.id = hj.id_humeur "
            "LEFT JOIN humeur_jours_status hjs ON hjs.id = hj.id_humeur_jours_status "
            "WHERE hj.id_user = ? "
            "ORDER BY hj.date_creation DESC",
            (id_user,)
        ).fetchall()
        return [dict(row) for row in rows]

# function router to find humeur jours today
@router.get("/api/humeur/jours/today")
def humeurJoursToday(utilisateur: dict = Depends(utilisateur_connecte)):
    humeurToday, humeurTodayCauses = findByDateJour(utilisateur["id"])

    return JSONResponse(
        status_code = 200,
        content = {
            "humeur_jours": humeurToday,
            "humeur_jours_causes": humeurTodayCauses
        }
    )
    
# function router to find All humeur jours
@router.get("/api/humeur/jours")
def humeurJours(utilisateur: dict = Depends(utilisateur_connecte)):
    humeurJours = findAll(utilisateur["id"])

    return JSONResponse(
        status_code = 200,
        content = {
            "data": humeurJours
        }
    )

# function router to get humeur jours by id
@router.get("/api/humeur/jours/{id_humeur_jours}")
def get_humeur_jours(id_humeur_jours: int = Path(gt=0), utilisateur: dict = Depends(utilisateur_connecte)):

    humeur_jours, humeur_jours_causes = findById(id_humeur_jours, utilisateur["id"])

    if humeur_jours is None:
        return JSONResponse(
            status_code=404,
            content={"message": "Cette humeur n'existe pas.", "errors": {}},
        )

    return JSONResponse(
        status_code=200,
        content={
            "humeur_jours": humeur_jours,
            "humeur_jours_causes": humeur_jours_causes,
        },
    )
# function router to insert new humeur jours
@router.post("/api/humeur/jours")
def create_humeurJours(data: HumeurJours, utilisateur: dict = Depends(utilisateur_connecte)):

    try:
        id_humeur_jours = create(data.id_humeur, data.note, data.id_humeur_causes, utilisateur["id"])

        return JSONResponse(
            status_code = 201,
            content = {
                "id_humeur_jours": id_humeur_jours
            }
        )
    
    except HumeurInconnue:
        return JSONResponse(status_code=422, content={
            "message": "Humeur invalide.",
            "errors": {"id_humeur": "Cette humeur n'existe pas."}
        })
    except CauseInconnue:
        return JSONResponse(status_code=422, content={
            "message": "Certaines informations ne sont pas valides.",
            "errors": {"id_humeur_causes": "Une des causes choisies n'existe pas."},
        })
 
