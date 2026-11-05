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

-- humeur 
CREATE TABLE IF NOT EXISTS humeur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    val INTEGER,
    desce TEXT
);

-- humeur_cause
CREATE TABLE IF NOT EXISTS humeur_cause (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    val TEXT,
    desce TEXT
);

-- humeur_jours
CREATE TABLE IF NOT EXISTS humeur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_humeur INT NOT NULL,
    date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
    note TEXT,
    FOREIGN KEY (id_humeur) REFERENCES humeur(id)
);

-- humeur_jours_causes
CREATE TABLE IF NOT EXISTS humeur_jours_causes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_humeur_jours INT NOT NULL,
    id_humeur_cause INT NOT NULL,
    FOREIGN KEY (id_humeur_jours) REFERENCES humeur_jours(id),
    FOREIGN KEY (id_humeur_cause) REFERENCES humeur_cause(id)
);