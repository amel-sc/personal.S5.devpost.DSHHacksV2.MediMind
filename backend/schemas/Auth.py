from typing import Literal, Annotated
from pydantic import BaseModel, StringConstraints
from datetime import date

# Modèle représentant le JSON attendu
class Inscription(BaseModel):
    pseudo: str
    mdp: str
    date_naissance: date

# Inscription error
class InscriptionError(Exception):
    pass