-- file: db/create_tables.sql
-- andrew jarcho
-- 2017-02-16

DROP TABLE IF EXISTS sl_night CASCADE;

CREATE TABLE sl_night (
    night_id SERIAL UNIQUE,
    start_date date NOT NULL,
    start_time time NOT NULL,
    PRIMARY KEY (night_id)
);


DROP TABLE IF EXISTS sl_nap;

CREATE TABLE sl_nap (
    nap_id SERIAL UNIQUE, 
    start_time time NOT NULL,
    duration interval NOT NULL,
    night_id integer NOT NULL,
    PRIMARY KEY (nap_id),
    FOREIGN KEY (night_id) REFERENCES sl_night (night_id)
);
