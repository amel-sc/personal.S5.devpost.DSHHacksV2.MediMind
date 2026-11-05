from typing import Literal
from pydantic import BaseModel

# Modèle for message
class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

# Modèle représentant le JSON attendu
class Request(BaseModel):
    message: str
    historique: list[Message]
    langue: Literal["fr", "en"]