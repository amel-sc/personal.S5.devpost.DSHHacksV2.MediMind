from typing import Literal
from pydantic import BaseModel

# Modèle représentant le JSON attendu
class HumeurJours(BaseModel):
    id_humeur: int
    note: str
    id_humeur_causes: list[int]

# Humeur Inconnue
class HumeurInconnue(Exception):
    pass