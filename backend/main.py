from typing import Literal
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from assistant import ask_medimind

app = FastAPI()

# Modèle for message
class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

# Modèle représentant le JSON attendu
class Request(BaseModel):
    message: str
    historique: list[Message]
    langue: Literal["fr", "en"]

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