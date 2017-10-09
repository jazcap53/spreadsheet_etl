## Spreadsheet ETL ##

#### I built this to keep track of my sleep pattern; it turned into something more. ####

Spreadsheet ETL now implements a pipeline that extracts data from a .csv file, transforms the data into a database-friendly format, and loads it into a PostgreSQL db.

The program let me experiment with concurrency in Python, and with writing testable code.

As of 2017-10-09, Spreadsheet ETL's Extract, Transform, and Load modules are all working properly. The pipelining strategy needs to be revamped; other changes are planned. I expect to return to this project frequently to refactor and learn.
