from fastapi import FastAPI
from api import Message, Conversation
from db.database import init_db

app = FastAPI()

# init database
@app.on_event("startup")
def startup():
    init_db()

app.include_router(Message.router)
app.include_router(Conversation.router)