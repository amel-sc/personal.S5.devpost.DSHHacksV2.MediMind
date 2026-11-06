import sqlite3
from fastapi import APIRouter
from schemas.HumeurJours import HumeurJours
from contextlib import closing
from services.assistant import ask_medimind
from fastapi.responses import JSONResponse
from db.database import get_connection

router = APIRouter()

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
            "SELECT * "
            "FROM humeur_jours ORDER BY date_creation DESC"
        ).fetchall()

        return [dict(row) for row in rows]

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
