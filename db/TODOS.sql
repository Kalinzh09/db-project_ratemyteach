CREATE TABLE schueler (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(250) NOT NULL,
    username VARCHAR(250) NOT NULL UNIQUE,
    password VARCHAR(250) NOT NULL
);

CREATE TABLE lehrer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(250) NOT NULL,
    name VARCHAR(250) NOT NULL,
    vorname VARCHAR(250) NOT NULL,
    fach VARCHAR(250) NOT NULL,
);

CREATE TABLE bewertung (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sterne VARCHAR(250) NOT NULL,
    datum VARCHAR(250) NOT NULL,
    schueler_id VARCHAR(250) NOT NULL,
    lehrer_id VARCHAR(250) NOT NULL
    FOREIGN KEY (schueler_id) REFERENCES schueler(id),
    FOREIGN KEY (lehrer_id) REFERENCES lehrer(id)
);

CREATE TABLE schuelerliste (

);
