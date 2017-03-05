# file: src/config.py
# andrew jarcho
# 2017-02-22

# python 2.7, 3.5


from configparser import ConfigParser


def config(filename='src/database.ini', section='postgresql'):
    """Read the configuration file for the db connection."""
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {} not found in the {} file'.format(section, filename))
    return db
