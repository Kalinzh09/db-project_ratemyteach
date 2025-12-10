CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(250) NOT NULL UNIQUE,
    password VARCHAR(250) NOT NULL
);

CREATE TABLE todos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    content VARCHAR(100),
    due DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE bewertung (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sterne VARCHAR(250) NOT NULL,
    datum VARCHAR(250) NOT NULL,
    schueler_id VARCHAR(250) NOT NULL,
    lehrer_id VARCHAR(250) NOT NULL
    FOREIGN KEY (schüler_id) REFRENCES schüler(id),
    FOREIGN KEY (lehrer_id) REFRENCES schüler(id)
);

CREATE TABLE schueler (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(250) NOT NULL,
    benutzername VARCHAR(250) NOT NULL,
);

CREATE TABLE lehrer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(250) NOT NULL,
    name VARCHAR(250) NOT NULL,
    vorname VARCHAR(250) NOT NULL,
    fach VARCHAR(250) NOT NULL,
);
