#!/usr/bin/python

"""
    SolarEdge API Interface
    - Gets (by default) HOURLY history data from SolarEdge monitoring API

    This is my first time building something with a class, so please be gentle ;)
"""

import logging
import requests


# Get logger
logger = logging.getLogger(__name__)


class SolarEdge:
    SITE_ID = None
    API_LINK = "https://monitoringapi.solaredge.com"

    def __init__(self, API_KEY, SITE_ID=None, request_count=0):
        logger.debug("Init SolarEdge")

        self.API_KEY = API_KEY
        self.SITE_ID = SITE_ID
        self.request_count = request_count

    def select_site_id(self, API_LINK=API_LINK):
        logger.debug("Querying the site_id(s)")

        # Send request to SolarEdge API
        self.request_count += 1
        r = requests.get(f"{API_LINK}/sites/list", params={"api_key": self.API_KEY})

        if r.status_code != 200:
            logger.critical(
                "Could not get sites list, error: {r.status_code} exiting..."
            )
            exit(-1)
        response = r.json()["sites"]

        # Collect all site_ids
        logger.info("Site ids found:")
        for site in response["site"]:
            logger.info(f'SiteId {site["id"]}: {site["name"]}')
        
        if response["count"] == 1:
            # Only one site, use this one and continue silently
            logger.info(f'Only one site_id found, using: {response["site"][0]["id"]}')
            self.SITE_ID = str(response["site"][0]["id"])
        else:
            # Multiple sites found, print and exit
            logger.warning("Multiple sites found")
            logger.info("Please enter one of the 'site_id' above in section 'SolarEdge'. Exiting...")
            exit(0)
