import sqlite3
from fastapi import APIRouter
from schemas.Message import RequestMessage
from contextlib import closing
from services.assistant import ask_medimind
from fastapi.responses import JSONResponse
from db.database import get_connection

router = APIRouter()

# function to get humeur
def findAll():
    with closing(get_connection()) as conn:
        rows = conn.execute(
            "SELECT * "
            "FROM humeur_cause ORDER BY id"
        ).fetchall()

        return [dict(row) for row in rows]

# router to get all humeur
@router.get("/api/humeur/cause")
def humeurCauses():
    humeurCauses = findAll()
    
    return JSONResponse(
        status_code = 200,
        content = {
            "data": humeurCauses
        }
    )
