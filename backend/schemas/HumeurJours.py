from typing import Literal, Annotated
from pydantic import BaseModel, StringConstraints

NOTE_MAX = 500

# Modèle représentant le JSON attendu
class HumeurJours(BaseModel):
    id_humeur: int
    note: Annotated[str, StringConstraints(strip_whitespace=True, max_length=NOTE_MAX)] = ""
    id_humeur_causes: list[int]

# Humeur Inconnue
class HumeurInconnue(Exception):
    pass

# Cause Inconnue
class CauseInconnue(Exception):
    pass