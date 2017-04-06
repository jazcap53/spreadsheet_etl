-- file: db/create_procedures.sql
-- andrew jarcho
-- 2017-04-05


CREATE OR REPLACE FUNCTION insert_fraction(numerator int, denominator int) RETURNS text AS $$
from plpy import spiexceptions
try:
    plan = plpy.prepare("INSERT INTO fractions (frac) VALUES ($1 / $2)", ["int", "int"])
    plpy.execute(plan, [numerator, denominator])
except spiexceptions.DivisionByZero:
    return "denominator cannot equal zero"
except spiexceptions.UniqueViolation:
    return "already have that fraction"
except plpy.SPIError, e:
    return "other error, SQLSTATE %s" % e.sqlstate
else:
    return "fraction inserted"
$$ LANGUAGE plpythonu;


DROP FUNCTION sl_insert_night(date, time without time zone);

CREATE FUNCTION sl_insert_night(new_start_date date, new_start_time time without time zone) RETURNS text AS $$
from plpy import spiexceptions
try:
    plan = plpy.prepare("INSERT INTO sl_night (start_date, start_time) VALUES($1, $2)", ["date", "time without time zone"])
    plpy.execute(plan, [new_start_date, new_start_time])
except plpy.SPIError, e:
    return "error: SQLSTATE %s" % (e.sqlstate,)
else:
    return "sl_insert_night() succeeded"
$$ LANGUAGE plpythonu;
