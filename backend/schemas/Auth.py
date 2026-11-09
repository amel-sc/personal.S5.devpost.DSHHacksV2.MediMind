from typing import Literal, Annotated
from pydantic import BaseModel, StringConstraints
from datetime import date

# Modèle représentant le JSON attendu
class Inscription(BaseModel):
    first_name: str
    last_name: str
    email: str
    mdp: str
    date_naissance: date

# Modèle représentant le JSON attendu
class Connexion(BaseModel):
    email: str
    mdp: str

# Inscription error
class InscriptionError(Exception):
    def __init__(self, champ: str, code: str):
        self.champ = champ
        self.code = code
        super().__init__(code)

# Connexion error
class ConnexionError(Exception):
    def __init__(self, champ: str, code: str):
        self.champ = champ
        self.code = code
        super().__init__(code)