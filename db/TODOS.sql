CREATE TABLE schueler (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(250) NOT NULL UNIQUE,
    username VARCHAR(250) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(250) NOT NULL UNIQUE
);

CREATE TABLE lehrer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(250) NOT NULL UNIQUE,
    vorname VARCHAR(250) NOT NULL,
    name VARCHAR(250) NOT NULL,
    fach VARCHAR(250) NOT NULL
);

CREATE TABLE bewertung (
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- Overall Score (wird aus Kategorien berechnet)
    sterne FLOAT NOT NULL CHECK (sterne BETWEEN 1 AND 5),

    -- Kategorien für Stats / Spiderchart
    verstandlichkeit FLOAT NOT NULL CHECK (verstandlichkeit BETWEEN 1 AND 5),
    fairness FLOAT NOT NULL CHECK (fairness BETWEEN 1 AND 5),
    sympathie FLOAT NOT NULL CHECK (sympathie BETWEEN 1 AND 5),
    organisation FLOAT NOT NULL CHECK (organisation BETWEEN 1 AND 5),
    fachwissen FLOAT NOT NULL CHECK (fachwissen BETWEEN 1 AND 5),

    kommentar TEXT,
    datum DATETIME DEFAULT CURRENT_TIMESTAMP,

    schueler_id INT NOT NULL,
    lehrer_id INT NOT NULL,

    FOREIGN KEY (schueler_id) REFERENCES schueler(id),
    FOREIGN KEY (lehrer_id) REFERENCES lehrer(id)
);

INSERT INTO schueler (email, username, password) VALUES
('john.pork@mng.ch', 'johnporkiscalling', 'hashed_pw_1'),
('lisa@test.de', 'lisa456', 'hashed_pw_2');

INSERT INTO lehrer (email, vorname, name, fach) VALUES
('lebron.james@mng.ch', 'Lebron', 'James', 'Sport'),
('peter.schmidt@mng.ch', 'Peter', 'Schmidt', 'Informatik'),
('peter.cheese@mng.ch', 'Peter', 'Cheese', 'Informatik');


INSERT INTO bewertung (sterne, kommentar, schueler_id, lehrer_id) VALUES
(5, 'Sehr guter Unterricht!', 1, 1),
(4, 'Erklärt verständlich', 2, 1),
(3, 'Ganz okay', 1, 2);

INSERT INTO admin (username) VALUES
('x');
