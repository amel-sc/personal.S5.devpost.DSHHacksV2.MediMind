from fastapi import FastAPI
from api import Message

app = FastAPI()

app.include_router(Message.router)