# Setup

## To run this app locally:

* Create a virtual env
    * Edit the new virtualenv's <your_venv>/bin/activate by inserting:
    ``` 
    PYTHONPATH='/<your>/<path>/<to>/spreadsheet_etl:/<your>/<path>/<to>/spreadsheet_etl/src:/<your>/<path>/<to>/spreadsheet_etl/src/extract'
    export PYTHONPATH
  
    DB_URL='postgresql://sp_etl:<your_secret>@localhost:5432/sleep'
    export DB_URL
  
    DB_URL_TEST='postgresql://sp_etl:<your_secret>@localhost:5432/sleep_test'
    export DB_URL_TEST
    ```

    
* Set up PostgreSQL
    * Create the db user `sp_etl`:
    ```
    $ psql template1 -U postgres
    template1=# \i db_any/create_user.sql
    template1=# ALTER USER sp_etl WITH PASSWORD '<secret>';
    template1=# \q
    ```
    * Login as the new user, and create the db's:
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
    * Populate the `sleep` db:  
    ```
    $ python src/mk_processes.py src/current_sheet.csv -s
    ```  
    Note the -s switch; without this `spreadsheet_etl` will not write to the `sleep` db.  
    Expected output:
    ```
    Starting TCP server...
    2020-03-17 10:26:12,318  INFO     extract start
    2020-03-17 10:26:17,322  INFO     transform start
    2020-03-17 10:26:23,378  INFO     load start
    2020-03-17 10:26:24,349  INFO     extract finish
    2020-03-17 10:26:24,630  INFO     transform finish
    2020-03-17 10:26:25,671  INFO     load finish 
    ``` 
    At present, expect to wait about 10 seconds after the output has been generated for the script to terminate.    
    The `sleep` db is now ready to be queried.  

* Run the tests:  
    ```
    $ pytest
    ```
