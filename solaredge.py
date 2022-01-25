#!/usr/bin/python

"""
    SolarEdge API Interface
    - Gets (by default) HOURLY history data from SolarEdge monitoring API

    This is my first time building something with a class, so please be gentle ;)
"""

import coloredlogs, logging
import configparser
import solaredge_api as se


# Start logger
logger = logging.getLogger(__name__)
coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s"
)


def start_solaredge_api():
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


solaredge = start_solaredge_api()

print(solaredge.request_count)