import sqlite3
from fastapi import APIRouter
from schemas.Message import RequestMessage, ConversationInconnue
from contextlib import closing
from services.assistant import ask_medimind
from fastapi.responses import JSONResponse
from db.database import get_connection

router = APIRouter()

# function to verify if conversation exist by id
def verifyConversationById(conn, id_conversation: int):
    row = conn.execute(
        "SELECT * FROM conversation "
        "WHERE id = ?",
        (id_conversation)
    )

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
    # transformer l'objet pydantic en dictionnaire { }
    reponse, langue = ask_medimind(data.message, [m.model_dump()  for m in data.historique], data.langue)

    # insert response in base
    id_message = create_message('assistant', reponse, data.id_conversation)

    return JSONResponse(
        status_code = 200,
        content = {
            "id_message": id_message,
            "role": "assistant",
            "content": reponse,
        }
    )