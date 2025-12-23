DROP TABLE student;
DROP TABLE fakultet;
DROP TABLE projekti;
DROP TABLE tehnologije;
DROP TABLE programski_jezik;


CREATE TABLE fakultet (
    id SERIAL PRIMARY KEY,
    naziv VARCHAR(50) NOT NULL
);

CREATE TABLE studijski_program (
    id SERIAL PRIMARY KEY,
    fakultet_id INTEGER NOT NULL,
    tip_studija VARCHAR(30) NOT NULL CHECK (
        tip_studija IN ('Osnovne studije', 'Master studije', 'Doktorske studije')
    ),
    godina INTEGER NOT NULL,
    datum_pocetka DATE NOT NULL,
    datum_kraja DATE,
    FOREIGN KEY (fakultet_id) REFERENCES fakultet(id)
);

CREATE TABLE student (
    id SERIAL PRIMARY KEY,
    ime VARCHAR(30) NOT NULL,
    prezime VARCHAR(30) NOT NULL,
    email varchar(50) NOT NULL,
    kontakt_telefon VARCHAR(20),
    studijski_program_id INTEGER NOT NULL,
    FOREIGN KEY (studijski_program_id) REFERENCES studijski_program(id)
);

CREATE TABLE projekti (
    id SERIAL PRIMARY KEY,
    datum_pocetka_izrade DATE NOT NULL,
    datum_kraja_izrade_projekta DATE,
    opis VARCHAR(1000) NOT NULL,
    id_studenta INTEGER NOT NULL,
    FOREIGN KEY (id_studenta) REFERENCES student(id)
);

CREATE TABLE tehnologija (
    id SERIAL PRIMARY KEY,
    naziv VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE student_tehnologija (
    student_id INTEGER NOT NULL,
    tehnologija_id INTEGER NOT NULL,
    PRIMARY KEY (student_id, tehnologija_id),
    FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
    FOREIGN KEY (tehnologija_id) REFERENCES tehnologija(id) ON DELETE CASCADE
);

INSERT INTO fakultet (naziv) VALUES
    ('Arhitektonski fakultet'),
    ('Građevinski fakultet'),
    ('Elektrotehnički fakultet'),
    ('Mašinski fakultet'),
    ('Poljoprivredni fakultet'),
    ('Rudarsko-geološki fakultet'),
    ('Saobraćajni fakultet'),
    ('Tehnički fakultet u Boru'),
    ('Tehnološko-metalurški fakultet'),
    ('Fakultet organizacionih nauka'),
    ('Šumarski fakultet'),
    ('Geografski fakultet'),
    ('Biološki fakultet'),
    ('Fakultet za fizičku hemiju'),
    ('Fizički fakultet'),
    ('Hemijski fakultet'),
    ('Matematički fakultet'),
    ('Medicinski fakultet'),
    ('Stomatološki fakultet'),
    ('Farmaceutski fakultet'),
    ('Fakultet veterinarske medicine'),
    ('Ekonomski fakultet'),
    ('Pravoslavni bogoslovski fakultet'),
    ('Fakultet za obrazovanje učitelja i vaspitača'),
    ('Fakultet bezbednosti'),
    ('Fakultet za specijalnu edukaciju i rehabilitaciju'),
    ('Fakultet političkih nauka'),
    ('Fakultet sporta i fizičkog vaspitanja'),
    ('Filozofski fakultet'),
    ('Filološki fakultet'),
    ('Pravni fakultet');
