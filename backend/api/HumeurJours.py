import sqlite3
from fastapi import APIRouter
from schemas.Message import RequestMessage
from contextlib import closing
from services.assistant import ask_medimind
from fastapi.responses import JSONResponse
from db.database import get_connection

router = APIRouter()

# function to insert new humeur jours
def create(id_humeur: int, note: str, humeur_causes: list[int]):
    with closing(get_connection()) as conn, conn:
        cur = conn.execute(
            "INSERT INTO humeur_jours (id_humeur, note) VALUES (?, ?)",
            (id_humeur, note)
        )
        id_humeur_jours = cur.lastrowid

        cur = conn.execute(
            "INSERT INTO humeur_jours_causes (id_humeur_jours, id_humeur_cause) VALUES (?, ?)",
            [(id_humeur_jours, id_humeur_cause) for id_humeur_cause in humeur_causes]
        )

    return id_humeur_jours
