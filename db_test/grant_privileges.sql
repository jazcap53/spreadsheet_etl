-- file: db_test/grant_privileges.sql
-- andrew jarcho
-- 2017-04-06

GRANT SELECT, UPDATE, INSERT, DELETE ON slt_nap, slt_night TO sp_etl;
GRANT USAGE ON slt_night_night_id_seq TO sp_etl;
GRANT USAGE ON slt_nap_nap_id_seq TO sp_etl;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO sp_etl;

-- GRANT SELECT, UPDATE, INSERT, DELETE ON slt_nap, slt_night TO andy;
-- GRANT USAGE ON slt_night_night_id_seq TO andy;
-- GRANT USAGE ON slt_nap_nap_id_seq TO andy;
