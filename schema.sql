DROP TABLE IF EXISTS workers;
CREATE TABLE workers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    middlename TEXT NOT NULL,
    birthday TEXT NOT NULL,
    gender TEXT NOT NULL,
    department_id INTEGER,
    email TEXT,
    archive INTEGER
);


DROP TABLE IF EXISTS departments;
CREATE TABLE departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

INSERT INTO departments VALUES (NULL, 'Администрация');
INSERT INTO departments VALUES (NULL, 'Отдел финансов');
INSERT INTO departments VALUES (NULL, 'Отдел ИТ');