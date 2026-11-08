from fastapi import FastAPI, Request
from api import Message, Conversation, Humeur, HumeurCause, HumeurJours
from db.database import init_db
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

# init database
@app.on_event("startup")
def startup():
    init_db()

# exception
@app.exception_handler(StarletteHTTPException)
async def erreur_http(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": str(exc.detail), "errors": {}},
        headers=exc.headers,
    )

app.include_router(Message.router)
app.include_router(Conversation.router)
app.include_router(Humeur.router)
app.include_router(HumeurCause.router)
app.include_router(HumeurJours.router)