-- file: db_s_etl/grant_privileges.sql
-- andrew jarcho
-- 2017-04-06

GRANT SELECT, UPDATE, INSERT, DELETE ON sl_nap, sl_night TO sp_etl;
GRANT USAGE ON sl_night_night_id_seq TO sp_etl;
GRANT USAGE ON sl_nap_nap_id_seq TO sp_etl;
