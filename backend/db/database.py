import sqlite3
from pathlib import Path

SCHEMA_PATH = "db/schema.sql"
DATABASE = "data/medimind.db"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row          # accès aux colonnes par nom
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db() -> None:
    Path(DATABASE).parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    try:
        conn.executescript(Path(SCHEMA_PATH).read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()

def get_db():
    """Dépendance FastAPI : une connexion par requête, fermée à la fin."""
    conn = get_connection()
    try:
        return conn
    finally:
        conn.close()