## Spreadsheet ETL ##

#### I built this to keep track of my sleep pattern; it's now a laboratory for trying out new coding ideas. ####

Spreadsheet ETL extracts data from a .csv file, transforms the data into a database-friendly format, and loads it into a PostgreSQL db.

The program lets me experiment with concurrency in Python, and with writing testable code.

As of 2017-11-29, Spreadsheet ETL's Extract, Transform, and Load modules are all working properly. The pipelining strategy needs to be revamped; other changes are planned including better data validation. I have been returning to this project frequently to refactor and learn.
