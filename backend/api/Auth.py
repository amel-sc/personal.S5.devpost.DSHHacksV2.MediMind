import sqlite3
from fastapi import APIRouter, Path
from contextlib import closing
from services.assistant import ask_medimind
from fastapi.responses import JSONResponse
from db.database import get_connection
from datetime import datetime, timedelta, timezone

router = APIRouter()

# function to get user pseudo
def findById(pseudo: str):
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