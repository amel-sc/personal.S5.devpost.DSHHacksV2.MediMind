from fastapi import APIRouter
from schemas.Message import Request
from contextlib import closing
from services.assistant import ask_medimind
from fastapi.responses import JSONResponse
from db.database import get_connection

router = APIRouter()

# function to insert messages
def create_message(message):
    with closing(get_connection()) as conn:
        conn.execute(
            "INSERT INTO messages (role, content, id_conversation) VALUES (?, ?)",
            (message.role, message.content, message.id_conversation)
        )
        conn.commit()

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