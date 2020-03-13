-- file: create_user.sql
-- andrew jarchho
-- 2020-03-12

DO $$
BEGIN
  CREATE ROLE sp_etl WITH CREATEDB LOGIN;
  EXCEPTION WHEN DUPLICATE_OBJECT THEN
  RAISE NOTICE 'not creating role sp_etl -- it already exists';
END
$$;