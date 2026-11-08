from typing import Literal
from pydantic import BaseModel

# Modèle for message
class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

# Modèle représentant le JSON attendu
class RequestMessage(BaseModel):
    message: str
    historique: list[Message]
    langue: Literal["fr", "en"]
    id_conversation: int | None = None

# Converation Inconnue
class ConversationInconnue(Exception):
    pass
