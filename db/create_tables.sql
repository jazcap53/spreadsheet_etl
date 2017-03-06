-- file: db/create_tables.sql
-- andrew jarcho
-- 2017-02-16

DROP TABLE IF EXISTS sl_night CASCADE;

CREATE TABLE sl_night (
    night_id SERIAL UNIQUE,
    start_date date NOT NULL,
    start_time time NOT NULL
);


DROP TABLE IF EXISTS sl_nap;

CREATE TABLE sl_nap (
    start_time time NOT NULL UNIQUE,
    duration interval NOT NULL,
    night_id INTEGER,
    PRIMARY KEY (start_time),
    FOREIGN KEY (night_id) REFERENCES sl_night (night_id)
);
