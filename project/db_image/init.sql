CREATE USER repl_user WITH REPLICATION LOGIN ENCRYPTED PASSWORD 'Qq12345';
SELECT pg_create_physical_replication_slot('replication_slot');

\connect labdatabase;

CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY, email VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS phone (
    id SERIAL PRIMARY KEY, phone_number VARCHAR(255) NOT NULL
);

INSERT INTO emails (email) VALUES ('blablabla@example.com'), ('kirill@gmail.com');
INSERT INTO phone (phone_number) VALUES ('89383832255'), ('89877462245');

