## Spreadsheet ETL ##

#### I built this to keep track of my sleep pattern; it turned into something more. ####

Spreadsheet ETL now implements a pipeline that extracts data from a .csv file, transforms the data into a database-friendly format, and loads it into a PostgreSQL database.

The program let me experiment with concurrency in Python, as well as code testability and unit testing.

As of 2017-06-25, Spreadsheet ETL's Extract, Transform, and Load modules all work; but a different approach to the pipelining aspect would have been more practical. I plan to come back to this program from time to time to refactor and learn. 
