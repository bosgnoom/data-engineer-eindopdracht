#!/usr/bin/python

"""
    Get produced energy data via SolarEdge API
    - Gets history data from SolarEdge monitoring API
    - Puts this data into a database
"""

import coloredlogs, logging
import configparser
import solaredge_api as se
import sqlite3
import datetime
import dateutil
import pprint
import time


# Start logger
logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s")


def start_solaredge_api():
    """
    Start the solaredge api
    Loads the API KEY from config.ini
    Checks and determines the siteId to use

    returns: reference to SolarEdge
    """

    # Use a config file to store the API KEY (so it's not hardwired into the code)
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Check if there's an API_KEY provided
    logger.debug("Checking for an API key in configfile")
    try:
        assert "api_key" in config["SolarEdge"]
    except:
        logger.critical(
            "No 'api_key' item found in config.ini, please add one! Exiting..."
        )
        exit(-1)
    else:
        logger.info("API key exists in configfile")

    # Check if there's already an SITE_ID
    logger.debug("Checking for a site id in configfile")
    try:
        # Fancy one...
        assert "site_id" in config["SolarEdge"]
    except AssertionError:
        logger.warning("No 'site_id' item found in config.ini")
    else:
        logger.info("Site id exists in configfile")

    # Initiate our SolarEdge class, the API key is mandatory
    # If there's a site_id, use it. Otherwise query the site_id
    if "site_id" in config["SolarEdge"]:
        # Init WITH site_id
        solaredge = se.SolarEdge(
            config["SolarEdge"]["api_key"], config["SolarEdge"]["site_id"]
        )
    else:
        # Init WITHOUT site_id
        solaredge = se.SolarEdge(config["SolarEdge"]["api_key"])

        # Get the available site_id(s) from the API key
        solaredge.select_site_id()

        # Store site_id for next run
        config["SolarEdge"]["site_id"] = solaredge.SITE_ID

        with open("config.ini", "w") as configfile:
            config.write(configfile)

    return solaredge


def prepare_tables(conn):
    """
    Creates tables for data (if not existing) on conn

    returns None
    """
    logger.debug("Create table for connections-per-day")
    sql = """CREATE TABLE IF NOT EXISTS connections ( 
                datum DATETIME PRIMARY KEY NOT NULL, 
                amount INT NOT NULL );
            """
    conn.execute(sql)

    logger.debug("Create table for solaredge history")
    sql = """CREATE TABLE IF NOT EXISTS history (
                tijdstip DATETIME PRIMARY KEY NOT NULL,
                energy FLOAT );
            """
    conn.execute(sql)

    conn.commit()


def get_amount_of_connections(conn):
    """
    Get the amount of requests to the SolarEdge API for today
    from conn
    """
    logger.debug("Getting the amount of requests for today")
    sql = "SELECT amount FROM connections WHERE datum = DATE('now');"
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()

    # Check result, act accordingly. Expects empty list or list with 1 item
    if len(result) == 0:
        logger.debug("No requests for today")
        return 0
    elif len(result) == 1:
        amount = result[0][0]
        logger.debug(f"Amount requests for today: {amount}")
        return amount
    else:
        logger.critical("More results returned than expected, exiting...")
        print(result)
        exit(-1)


def save_amount_of_connections(conn, n):
    """
    Saves the amount of requests to the database
    to conn
    """
    logger.debug(f"Saving the amount of requests ({n}) for today")
    sql = f"INSERT OR REPLACE INTO connections VALUES ( DATE('now'), '{n}' );"
    conn.execute(sql)
    conn.commit()


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


def fetch_all_data(solaredge, conn):
    """
    Fetch data from SolarEdge
    Store in database

    Loop over each month since (beginning of time)
    until yesterday
    """
    # Determine where to start with fetching data
    # - Check last date from database
    #   - No date --> starting date from API
    #   - Date --> starting date from database

    last_date = get_last_date(conn)
    if last_date is None:
        start_date = solaredge.get_start_date()
    else:
        logger.debug(f"Last date in database: {last_date}")

        # Round date to whole day, add one day extra
        # Should result in e.g. 30-09-2019 --> 01-10-2019
        start_date = datetime.date(
            last_date.year, last_date.month, last_date.day
        ) + datetime.timedelta(days=1)

    logger.info(f"Starting data import from: {start_date}")
    
    # Start looping over months
    while start_date <= (datetime.date.today() - datetime.timedelta(days=1)):
        logger.info("")
        
        # Extract last-day-of-month from start date (e.g: 16-09-2019: 01-09-2019 -> 30-09-2019)
        start_month = datetime.date(start_date.year, start_date.month, 1)
        stop_date = start_month + dateutil.relativedelta.relativedelta(
            months=1, days=-1
        )

        # Catch running until now
        if stop_date > datetime.date.today():
            stop_date = datetime.date.today() - datetime.timedelta(days=1)

        logger.info(f"Stopping data import on: {stop_date}")

        # Get one month of data
        data = solaredge.get_production(start_date, stop_date)
        records = []
        for item in data:
            # data is a list of dicts {'date': '2019-09-30 23:00:00', 'value': None}, where
            # value is either None, or a number

            tijdstip = dateutil.parser.parse(item["date"])
            if item["value"] != None:
                energie = int(item["value"])
            else:
                energie = 0

            records.append((tijdstip, energie))

        # Send data to database
        cursor = conn.cursor()
        cursor.executemany("INSERT INTO history VALUES (?, ?);", records)
        logging.info(f"Entered {cursor.rowcount} records into database")

        conn.commit()

        # Cool down and contemplate
        time.sleep(1)

        # Set for next month
        start_date = stop_date + datetime.timedelta(days=1)
    else:
        # Ja, er kan een _else_ in een _while_ loop
        logger.info("No data needs to be fetched (anymore)")

    logger.info("Data fetching complete!")


def get_data():
    # First, start the solaredge api:
    # - Opens config.ini and reads the API key
    # - The site_id is automatically determined and saved
    solaredge = start_solaredge_api()

    # Open database
    # Separate from class SolarEdge, to provide easy switching of databases
    # SQLite3 for now, keep data local (will be pushed into github repo)
    conn = sqlite3.connect("solaredge.db")

    # Prepare tables in database, only needed for first run
    prepare_tables(conn)

    # Database is connected, restore amount of connections for today
    solaredge.request_count = get_amount_of_connections(conn)

    # Fetch all data from solaredge, store in database
    fetch_all_data(solaredge, conn)

    # Clean up
    # Save amount of requests for today
    save_amount_of_connections(conn, solaredge.request_count)

    # Close connection to database
    conn.close()

# Wrap get_data into __main__, so this function can be
# called through an "import ophalen_solaredge"
if __name__ == "__main__":
    get_data()
