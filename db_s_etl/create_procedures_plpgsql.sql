-- file: db_s_etl/create_procedures.sql
-- andrew jarcho
-- 2017-04-05


CREATE OR REPLACE FUNCTION sl_insert_night(new_start_date date,
    new_start_time time without time zone,
    new_start_no_data boolean,
    new_end_no_data boolean) RETURNS text AS $$
DECLARE
  sl_night_row sl_night%ROWTYPE;

BEGIN
    SELECT * INTO sl_night_row FROM sl_night WHERE start_date = new_start_date AND
                                                   start_time = new_start_time AND
                                                   start_no_data = new_start_no_data AND
                                                   end_no_data = new_end_no_data;
    IF FOUND THEN
        RETURN 'sl_insert_night() failed: row already in table';
    END IF;

    INSERT INTO sl_night (night_id, start_date, start_time, start_no_data, end_no_data)
    values (nextval('sl_night_night_id_seq'), new_start_date, new_start_time, new_start_no_data,
            new_end_no_data);
    RETURN 'sl_insert_night() succeeded';

    EXCEPTION
        WHEN OTHERS THEN
            RETURN 'error inserting night into db';
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION sl_insert_nap(new_start_time time without time zone,
                                         new_duration interval hour to minute,
                                         new_night_id integer)
                                         RETURNS text AS $$

DECLARE
    sl_nap_row sl_nap%ROWTYPE;
    fk_night_id INTEGER;

BEGIN
    SELECT * INTO sl_nap_row FROM sl_nap WHERE start_time = new_start_time AND
                                               duration = new_duration AND
                                               night_id = new_night_id;

    IF FOUND THEN
        RETURN 'sl_insert_nap() failed: row already in table';
    END IF;

    SELECT currval('sl_night_night_id_seq') INTO fk_night_id;

    INSERT INTO sl_nap (nap_id, start_time, duration, night_id)
    VALUES (nextval('sl_nap_nap_id_seq'), new_start_time, new_duration, fk_night_id);
    RETURN 'sl_insert_nap() succeeded';

    EXCEPTION
        WHEN OTHERS THEN
            RETURN 'error inserting nap into db';

END;
$$ LANGUAGE plpgsql;
