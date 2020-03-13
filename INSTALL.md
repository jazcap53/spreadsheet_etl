### this file just has a few notes at present

Set up the Postgresql database:
    psql template1 -U postgres
    \i db_any/create_user.sql
    ALTER USER sp_etl WITH PASSWORD '<secret>';
    \q
    
    psql template1 -U sp_etl
    create database sleep
    create database sleep_test
    \c sleep
    \i db_s_etl/create_tables.sql
    \i db_s_etl/create_procedures_plpgsql.sql
    \i db_s_etl/grant_privileges.sql
    \c sleep_test
    \i db_test/create_tables.sql
    \i db_test/create_procedures_plpgsql.sql
    \i db_test/grant_privileges.sql
    \q
    
    
    
    