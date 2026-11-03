from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from assistant import ask_medimind

app = FastAPI()

# Modèle représentant le JSON attendu
class MessageRequest(BaseModel):
    message: str
    langue: str

@app.post("/api/message/send")
def traitement_message(data: MessageRequest):
    question = data.message
    langue_recu = data.langue

    reponse, langue = ask_medimind(question, langue_recu)

    return JSONResponse(
        status_code = 200,
        content = {
            "sender": "medimind",
            "content": reponse,
        }
    )