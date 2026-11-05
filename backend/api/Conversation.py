import sqlite3
from fastapi import APIRouter
from schemas.Message import RequestMessage
from contextlib import closing
from services.assistant import ask_medimind
from fastapi.responses import JSONResponse
from db.database import get_connection

router = APIRouter()

# function to get conversation
def findAll():
    with closing(get_connection()) as conn:
        rows = conn.execute(
            "SELECT id, date, first_message "
            "FROM conversation ORDER BY date_creation DESC"
        ).fetchall()

        return [dict(row) for row in rows]

# function to insert conversation
def create_conversation(first_message: str):
    with closing(get_connection()) as conn, conn:
        cur = conn.execute(
            "INSERT INTO conversation (first_message) VALUES (?)",
            (first_message,)
        )
        return cur.lastrowid