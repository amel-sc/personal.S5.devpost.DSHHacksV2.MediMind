import sqlite3
from fastapi import APIRouter, Path
from contextlib import closing
from services.assistant import ask_medimind
from fastapi.responses import JSONResponse
from db.database import get_connection
from datetime import date, datetime, timedelta, timezone
from utils.PasswordUtil import hash_password, verifier_mot_de_passe

router = APIRouter()

# function to get user pseudo
def findByPseudo(pseudo: str):
    with closing(get_connection()) as conn:
        row = conn.execute(
            "SELECT * FROM utilisateur "
            "WHERE pseudo = ? "
            "LIMIT = 1",
            (pseudo,)
        ).fetchone()

        if row is None:
            return None

    return dict(row)

# function to create new user
def create(pseudo: str, date_naissance: date, mdp: str):
    with closing(get_connection()) as conn:
        row = conn.execute(
           "INSERT INTO utilisateur (pseudo, date_naissance, mdp) VALUES (?, ?, ?)"
           (pseudo, date_naissance.isoformat(), hash_password(mdp)) 
        )

# function to get user by pseudo and mdp

