import sqlite3
from fastapi import APIRouter, Path, Depends, HTTPException, Request, status
from contextlib import closing
from services.assistant import ask_medimind
from fastapi.responses import JSONResponse
from db.database import get_connection
from datetime import date, datetime, timedelta, timezone
from utils.PasswordUtil import hash_password, verifier_mot_de_passe
from schemas.Auth import Inscription, InscriptionError, ConnexionError, Connexion

router = APIRouter()

# function to verify utilisateur in session
def utilisateur_connecte(request: Request):
    user_id = request.session.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié",
        )

    utilisateur = findById(user_id)

    if utilisateur is None:
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session invalide",
        )

    return utilisateur

# function to get user by id
def findById(user_id: str):
    with closing(get_connection()) as conn:
        row = conn.execute(
            "SELECT * FROM utilisateur "
            "WHERE id = ? "
            "LIMIT 1",
            (user_id,)
        ).fetchone()

    return dict(row)

# function to verify user mail and password
def verify_auth(email: str, mdp: str):
    # verify email exist
    with closing(get_connection()) as conn, conn:
        emailNotExist = findByEmail(conn, email)

        if emailNotExist is None:
            raise ConnexionError("email", "emailInexistant")

        # verify mdp
        if verifier_mot_de_passe(mdp, emailNotExist["mdp"]) is False:
            raise ConnexionError("mdp", "mdpIncorrect")

    return emailNotExist

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
            raise InscriptionError("email", "emailExiste")

        row = conn.execute(
           "INSERT INTO utilisateur (first_name, last_name, email, date_naissance, mdp) VALUES (?, ?, ?, ?, ?)",
           (first_name, last_name, emailNormalize, date_naissance.isoformat(), hash_password(mdp)) 
        )

# function router to do connexion
@router.post("/api/connexion")
def connexion(data: Connexion, request: Request):
    try:
        user = verify_auth(data.email, data.mdp)

        request.session["user_id"] = user["id"]

        return JSONResponse(status_code=200, content={
            "message": "Connexion réussi",
            "user": {
                "id": user["id"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "email": user["email"],
                "date_naissance": user["date_naissance"],
            }
        })

    except ConnexionError as e:
        return JSONResponse(status_code=422, content={
            "message": "Certaines informations ne sont pas valides.",
            "errors": {
                e.champ: e.code
            },
        })

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
                e.champ: e.code
            },
        })
