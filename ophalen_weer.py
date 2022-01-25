#!/usr/bin/python3

"""
    Ophalen uurgemiddelde van het weer
    Bron: KNMI 
"""

import coloredlogs, logging
import requests
import sqlite3
import datetime, dateutil


def get_last_date(conn):
    """
    Get the latest date with information
    from conn
    else return None
    """
    logger.debug("Getting the latest date from database")
    sql = "SELECT tijdstip FROM history ORDER BY tijdstip DESC LIMIT 1;"
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()

    # Check result, act accordingly. Expects empty list or list with 1 item
    if len(result) == 0:
        logger.debug("No results found in database")
        return None
    elif len(result) == 1:
        return dateutil.parser.parse(result[0][0])
    else:
        logger.critical("More results returned than expected, exiting...")
        print(result)
        exit(-1)


# Start logger
logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s")

# Connect to sqlite3 database
conn = sqlite3.connect("knmi.db")

start_date = "20190916"
end_date = "20190917"

r = requests.get(
    "https://www.daggegevens.knmi.nl/klimatologie/uurgegevens",
    params={
        "start": start_date,
        "end": end_date,
        "vars": "ALL",
        "stns": 377,
        "fmt": "json",
    },
)

import pprint
respons = r.json()
