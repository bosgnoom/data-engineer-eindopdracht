#!/usr/bin/python3

"""
    Fetch historical weather data
    Source: KNMI 
"""

import coloredlogs, logging
import requests
import sqlite3
import datetime, dateutil
import pandas as pd


# Start logger
logger = logging.getLogger(__name__)
coloredlogs.install(level="INFO", fmt="%(asctime)s %(levelname)s %(message)s")


def get_solaredge_date_range(conn):
    """
        Get first and last date (as in datum) from solaredge database

        :return first, last date for weather history to fetch
    """
    logger.info("Getting the dates from solaredge database")

    cursor = conn.cursor()

    sql = "SELECT tijdstip FROM solaredge_history ORDER BY tijdstip ASC LIMIT 1;"
    cursor.execute(sql)
    start_date = dateutil.parser.parse(cursor.fetchone()[0])

    sql = "SELECT tijdstip FROM solaredge_history ORDER BY tijdstip DESC LIMIT 1;"
    cursor.execute(sql)
    end_date = dateutil.parser.parse(cursor.fetchone()[0])

    logger.debug(f'Found {start_date} and {end_date}')

    return start_date, end_date


def get_knmi_last_date(conn):
    """
        Gets last date entry in knmi database
        :param conn: database connection 
        :return date or None
    """
    logger.info("Getting the last date from knmi database")

    cursor = conn.cursor()
    sql = "SELECT date FROM knmi_history ORDER BY date DESC LIMIT 1;"

    try:
        cursor.execute(sql)
    except sqlite3.Error as e:
        logger.warning(f'Error: no result from database: {e}')
        return None

    last_date = dateutil.parser.parse(cursor.fetchone()[0])

    logger.debug(f'Result from knmi database call: {last_date}')
    
    return last_date


def get_data():
    # Connect to database
    conn = sqlite3.connect('database.db')

    # Get last date from knmi database
    last_knmi = get_knmi_last_date(conn)

    # Get dates from solaredge database
    first_solar, last_solar = get_solaredge_date_range(conn)

    # Determine which starting date to use
    if last_knmi is None:
        logger.debug('No date from KNMI, using solaredge as starting date')
        first_date = first_solar
    else:
        logger.debug('KNMI returned a date, using this one as starting date')
        first_date = last_knmi

    # Convert dates into knmi format
    start_date = first_date.strftime('%Y%m%d')
    end_date = last_solar.strftime('%Y%m%d')

    # Is a fetch needed?
    if start_date == end_date:
        logger.info('No data needs to be fetched from KNMI, skipping query...')
    else:
        logger.debug(f'Querying KNMI for dates {start_date} to {end_date}')

        # API call to KNMI, just get all data for now.
        # TODO: Optimize, only request parameters which will be put into model
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

        # Convert the JSON to a DataFrame
        logger.info('JSON to DataFrame')
        weather_history = pd.DataFrame.from_dict(r.json())

        # Save to database
        logger.info('DataFrame to database')
        weather_history.to_sql('knmi_history', con=conn , if_exists='append',
                index_label='id')

    # Close connection to database
    conn.commit()
    conn.close()


# Wrap get_data into __main__, so this function can be
# called through an "import ophalen_weer"
if __name__ == "__main__":
    get_data()
