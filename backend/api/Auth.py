import sqlite3
from fastapi import APIRouter, Path
from contextlib import closing
from services.assistant import ask_medimind
from fastapi.responses import JSONResponse
from db.database import get_connection
from datetime import date, datetime, timedelta, timezone
from utils.PasswordUtil import hash_password, verifier_mot_de_passe
from schemas.Auth import Inscription, InscriptionError

router = APIRouter()

# function to get user email
def findByEmail(conn, email: str):
    row = conn.execute(
        "SELECT * FROM utilisateur "
        "WHERE email = ? "
        "LIMIT 1",
        (email,)
    ).fetchone()

    if row is None:
        return None

    return dict(row)

# function to create new user
def create(first_name: str, last_name: str, email: str, date_naissance: date, mdp: str):
    emailNormalize = email.strip().lower()

    with closing(get_connection()) as conn, conn:

        exist = findByEmail(conn, emailNormalize)

        if exist is not None:
            raise InscriptionError("email", "emailExist")

        row = conn.execute(
           "INSERT INTO utilisateur (first_name, last_name, email, date_naissance, mdp) VALUES (?, ?, ?, ?, ?)",
           (first_name, last_name, emailNormalize, date_naissance.isoformat(), hash_password(mdp)) 
        )

# function router to create new user
@router.post("/api/inscription")
def inscription(data: Inscription):
    try:
        create(data.first_name, data.last_name, data.email, data.date_naissance, data.mdp)
        return JSONResponse(
            status_code=201,
            content={
                "message": "Inscription réussi",
                "errors": {}
            }
        )

    except InscriptionError as e:
        return JSONResponse(status_code=422, content={
            "message": "Certaines informations ne sont pas valides.",
            "errors": {
                e.champ: e.message
            },
        })
