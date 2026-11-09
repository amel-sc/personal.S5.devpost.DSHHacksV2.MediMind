-- utilisateur
CREATE TABLE IF NOT EXISTS utilisateur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    email TEXT UNIQUE,
    mdp TEXT,
    date_naissance TEXT,
    date_creatin TEXT DEFAULT CURRENT_TIMESTAMP
);

-- conversation
CREATE TABLE IF NOT EXISTS conversation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
    first_message TEXT,
    id_user INTEGER,
    FOREIGN KEY (id_user) REFERENCES utilisateur(id)
);

-- message
CREATE TABLE IF NOT EXISTS message (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL CHECK (role IN ('assistant', 'user')),
    content TEXT NOT NULL,
    id_conversation INTEGER NOT NULL,
    alerte INTEGER NOT NULL DEFAULT 0 CHECK (alerte IN (0, 1)),
    FOREIGN KEY (id_conversation) REFERENCES conversation(id)
);

-- humeur 
CREATE TABLE IF NOT EXISTS humeur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    val INTEGER UNIQUE,
    desce TEXT
);

-- humeur_cause
CREATE TABLE IF NOT EXISTS humeur_cause (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    val TEXT,
    desce TEXT,
    code TEXT UNIQUE
);

-- humeur_jours_status
CREATE TABLE IF NOT EXISTS humeur_jours_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    val INTEGER,
    desce TEXT
);

-- humeur_jours
CREATE TABLE IF NOT EXISTS humeur_jours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_humeur INTEGER NOT NULL,
    date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
    note TEXT,
    id_humeur_jours_status INTEGER,
    id_user INTEGER,
    FOREIGN KEY (id_user) REFERENCES utilisateur(id),
    FOREIGN KEY (id_humeur) REFERENCES humeur(id),
    FOREIGN KEY (id_humeur_jours_status) REFERENCES humeur_jours_status(id)
);

-- humeur_jours_causes
CREATE TABLE IF NOT EXISTS humeur_jours_causes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_humeur_jours INTEGER NOT NULL,
    id_humeur_cause INTEGER NOT NULL,
    FOREIGN KEY (id_humeur_jours) REFERENCES humeur_jours(id),
    FOREIGN KEY (id_humeur_cause) REFERENCES humeur_cause(id)
);