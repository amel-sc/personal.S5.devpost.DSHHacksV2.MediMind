from typing import Literal, Annotated
from pydantic import BaseModel, StringConstraints

# Modèle représentant le JSON attendu
class Inscription(BaseModel):
    pseudo: str
    mdp: str
    date_naissance: str