import sqlite3
from fastapi import APIRouter, Path
from schemas.HumeurJours import HumeurJours
from contextlib import closing
from services.assistant import ask_medimind
from fastapi.responses import JSONResponse
from db.database import get_connection

router = APIRouter()

# function to find humeur_jours by id
def findById(id: int):
    with closing(get_connection()) as conn, conn:
        row = conn.execute(
            "SELECT hj.id, hj.note, hj.date_creation, "
            "       h.val   AS humeur_val, "
            "       h.desce AS humeur_desce "
            "FROM humeur_jours hj "
            "LEFT JOIN humeur h ON h.id = hj.id_humeur "
            "WHERE hj.id = ?",
            (id,)
        ).fetchone()

        row_causes = conn.execute(
            "SELECT hjc.id, hc.id, hc.val AS cause_val, hc.desce AS cause_desce "
            "FROM humeur_jours_causes hjc "
            "LEFT JOIN humeur_cause hc ON hc.id = hjc.id_humeur_cause "
            "WHERE id_humeur_jours = ?",
            (id,)
        ).fetchall()

    return (dict(row), [dict(row_cause) for row_cause in row_causes])

# function to insert new humeur jours
def create(id_humeur: int, note: str, humeur_causes: list[int]):
    with closing(get_connection()) as conn, conn:
        cur = conn.execute(
            "INSERT INTO humeur_jours (id_humeur, note) VALUES ((SELECT id FROM humeur WHERE val = ?), ?)",
            (id_humeur, note)
        )
        id_humeur_jours = cur.lastrowid

        cur = conn.executemany(
            "INSERT INTO humeur_jours_causes (id_humeur_jours, id_humeur_cause) VALUES (?, ?)",
            [(id_humeur_jours, id_humeur_cause) for id_humeur_cause in humeur_causes]
        )

    return id_humeur_jours

# function to findAll humeur jours 
def findAll():
    with closing(get_connection()) as conn:
        rows = conn.execute(
            "SELECT hj.id, hj.note, hj.date_creation, "
            "       h.val   AS humeur_val, "
            "       h.desce AS humeur_desce "
            "FROM humeur_jours hj "
            "LEFT JOIN humeur h ON h.id = hj.id_humeur "
            "ORDER BY hj.date_creation DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    
# function router to find All humeur jours
@router.get("/api/humeur/jours")
def humeurJours():
    humeurJours = findAll()

    return JSONResponse(
        status_code = 200,
        content = {
            "data": humeurJours
        }
    )

# function router to get humeur jours by id
@router.get("/api/humeur/jours/{id_humeur_jours}")
def get_humeur_jours(id_humeur_jours: int = Path(gt=0)):
    humeur_jours, humeur_jours_causes = findById(id_humeur_jours)

    return JSONResponse(
        status_code = 200,
        content = {
            "humeur_jours": humeur_jours,
            "humeur_jours_causes": humeur_jours_causes
        }
    )

# function router to insert new humeur jours
@router.post("/api/humeur/jours")
def create_humeurJours(data: HumeurJours):
    id_humeur_jours = create(data.id_humeur, data.note, data.id_humeur_causes)

    return JSONResponse(
        status_code = 200,
        content = {
            "id_humeur_jours": id_humeur_jours
        }
    )
