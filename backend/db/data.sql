-- humeur data
INSERT INTO humeur (val, desce) VALUES 
(1, 'Très bien'),
(2, 'Bien'),
(3, 'Bof'),
(4, 'Mal'),
(5, 'Très mal');

-- humeur_cause data
INSERT INTO humeur_cause (val, desce, code) VALUES
('Sommeil', 'Sommeil', 'sommeil'),
('Stress', 'Stress', 'stress'),
('Famille', 'Famille', 'famille'),
('Études', 'Études', 'etudes'),
('Amis', 'Amis', 'amis'),
('Santé', 'Santé', 'sante'),
('Couple', 'Couple', 'couple'),
('Autre', 'Autre', 'autre');

-- humeur_jours_status data
INSERT INTO humeur_jours_status (val, desce) VALUES
(1, 'Du jours'),
(2, 'Autre');