-- conversation
CREATE TABLE IF NOT EXISTS conversation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
    first_message TEXT
);

-- message
CREATE TABLE IF NOT EXISTS message (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL CHECK (role IN ('assistant', 'user')),
    content TEXT NOT NULL,
    id_conversation INTEGER NOT NULL,
    FOREIGN KEY (id_conversation) REFERENCES conversation(id)
);