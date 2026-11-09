import sqlite3
from pathlib import Path

# Chemin absolu du projet
BASE_DIR = Path(__file__).resolve().parent.parent

SCHEMA_PATH = BASE_DIR / "db" / "schema.sql"
SEED_PATH = BASE_DIR / "db" / "seed.sql"
DATABASE = BASE_DIR / "data" / "medimind.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    DATABASE.parent.mkdir(parents=True, exist_ok=True)

    conn = get_connection()

    try:
        # Création des tables
        conn.executescript(
            SCHEMA_PATH.read_text(encoding="utf-8")
        )

        # Insertion des données initiales
        conn.executescript(
            SEED_PATH.read_text(encoding="utf-8")
        )

        conn.commit()

    finally:
        conn.close()


def get_db():
    """Dépendance FastAPI : une connexion par requête."""
    conn = get_connection()
    try:
        return conn
    finally:
        conn.close()