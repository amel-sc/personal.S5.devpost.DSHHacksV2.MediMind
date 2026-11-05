from fastapi import APIRouter
from schemas.Message import Request
from services.assistant import ask_medimind
from fastapi.responses import JSONResponse

router = APIRouter()

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