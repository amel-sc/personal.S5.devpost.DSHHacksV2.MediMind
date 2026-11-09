-- db/seed.sql

-- humeur
INSERT OR IGNORE INTO humeur (val, desce) VALUES 
(1, 'Très bien'),
(2, 'Bien'),
(3, 'Bof'),
(4, 'Mal'),
(5, 'Très mal');


-- humeur_cause
INSERT OR IGNORE INTO humeur_cause (val, desce, code) VALUES
('Sommeil', 'Sommeil', 'sommeil'),
('Stress', 'Stress', 'stress'),
('Famille', 'Famille', 'famille'),
('Études', 'Études', 'etudes'),
('Amis', 'Amis', 'amis'),
('Santé', 'Santé', 'sante'),
('Couple', 'Couple', 'couple'),
('Autre', 'Autre', 'autre');


-- humeur_jours_status
-- On vérifie manuellement l'existence puisque val n'est pas UNIQUE.
INSERT INTO humeur_jours_status (val, desce)
SELECT 1, 'Du jours'
WHERE NOT EXISTS (
    SELECT 1 FROM humeur_jours_status WHERE val = 1
);

INSERT INTO humeur_jours_status (val, desce)
SELECT 2, 'Autre'
WHERE NOT EXISTS (
    SELECT 1 FROM humeur_jours_status WHERE val = 2
);