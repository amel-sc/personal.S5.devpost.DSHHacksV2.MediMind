import sqlite3
from fastapi import APIRouter
from schemas.Message import Request
from contextlib import closing
from services.assistant import ask_medimind
from fastapi.responses import JSONResponse
from db.database import get_connection

router = APIRouter()

# function to create conversation with message
def create_conversation_message(role: str, content: str):
    with closing(get_connection()) as conn, conn:
        cur = conn.execute(
            "INSERT INTO conversation (first_message) VALUES (?)",
            (content)
        )
        id_conversation = cur.lastrowid

        cur = conn.execute(
            "INSERT INTO message (role, content, id_conversation) VALUES (?, ?)",
            (role, content, id_conversation)
        )

    return id_conversation

# function to insert conversation
def create_conversation(first_message: str):
    with closing(get_connection()) as conn, conn:
        cur = conn.execute(
            "INSERT INTO conversation (first_message) VALUES (?)",
            (first_message)
        )
        return cur.lastrowid

# function to insert message
def create_message(role: str, content: str, id_conversation: int):
    with closing(get_connection()) as conn, conn:
        cur = conn.execute(
            "INSERT INTO message (role, content, id_conversation) VALUES (?, ?)",
            (role, content, id_conversation)
        )
        return cur.lastrowid

@router.post("/api/message")
def traitement_message(data: Request):
    # transformer l'objet pydantic en dictionnaire { }
    reponse, langue = ask_medimind(data.message, [m.model_dump()  for m in data.historique], data.langue)

    return JSONResponse(
        status_code = 200,
        content = {
            "role": "assistant",
            "content": reponse,
        }
    )