import sqlite3
from typing import Literal
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from backend.services.assistant import ask_medimind

app = FastAPI()

DATABASE = "database/medimind.db"

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    # Pour utiliser les foreign key
    conn.execute("PRAGMA foreign_keys = ON")

    return conn

@app.post("/api/message/send")
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