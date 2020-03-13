# Setup

## To run this app locally:

* Create a virtual env
* Set up PostgreSQL
    * Create the db user `sp_etl`
    ```
    $ psql template1 -U postgres
    template1=# \i db_any/create_user.sql
    template1=# ALTER USER sp_etl WITH PASSWORD '<secret>';
    template1=# \q
    ```
    * Login as the new user, and create the db's
    ```
    $ psql template1 -U sp_etl
    template1=> create database sleep
    template1=> create database sleep_test
    template1=> \c sleep
    sleep=> \i db_s_etl/create_tables.sql
    sleep=> \i db_s_etl/create_procedures_plpgsql.sql
    sleep=> \i db_s_etl/grant_privileges.sql
    sleep=> \c sleep_test
    sleep_test=> \i db_test/create_tables.sql
    sleep_test=> \i db_test/create_procedures_plpgsql.sql
    sleep_test=> \i db_test/grant_privileges.sql
    sleep_test=> \q
    ```
    * Populate the `sleep` db  
    ```
    $ python src/mk_processes.py src/current_sheet.csv -s
    ```  
    Note the -s switch; without this `spreadsheet_etl` will not write to the db  
The `sleep` db is now ready to be queried.  

* Run the tests  
    ```
    $ pytest
    ```  
Note: at present, each run of the tests adds one line to each of the two tables in `sleep_test`.
      