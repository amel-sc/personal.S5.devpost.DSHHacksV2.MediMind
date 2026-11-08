from fastapi import FastAPI, Request
from api import Message, Conversation, Humeur, HumeurCause, HumeurJours
from db.database import init_db
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from schemas.Message import ConversationInconnue

app = FastAPI()

# init database
@app.on_event("startup")
def startup():
    init_db()

# exceptions
@app.exception_handler(StarletteHTTPException)
async def erreur_http(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": str(exc.detail), "errors": {}},
        headers=exc.headers,
    )

@app.exception_handler(ConversationInconnue)
async def conversation_inconnue(request: Request, exc: ConversationInconnue):
    return JSONResponse(
        status_code=404,
        content={
            "code": "conversation_inconnue",
            "message": "Cette conversation n'existe pas.", 
            "errors": {}
        },
    )

app.include_router(Message.router)
app.include_router(Conversation.router)
app.include_router(Humeur.router)
app.include_router(HumeurCause.router)
app.include_router(HumeurJours.router)