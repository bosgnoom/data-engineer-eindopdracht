#!/usr/bin/python

"""
    SolarEdge API Interface
    - Gets (by default) HOURLY history data from SolarEdge monitoring API

    This is my first time building something with a class, so please be gentle ;)
"""

import logging
import requests
import pprint
import datetime
from dateutil.parser import parse

# Get logger
logger = logging.getLogger(__name__)


class SolarEdge:
    SITE_ID = None
    API_LINK = "https://monitoringapi.solaredge.com"

    def __init__(self, API_KEY, SITE_ID=None, request_count=0, start_date=None, end_date=None):
        logger.debug("Init SolarEdge")

        self.API_KEY = API_KEY
        self.SITE_ID = SITE_ID
        self.request_count = request_count
        self.start_date = start_date
        self.end_date = end_date


    def _api_call(self, url, params):
        """
            Performs a request to SolarEdge API
            Returns request response
        """
        # Check amount of requests 
        self.request_count += 1
        if self.request_count > 250:
            logger.warning("Too many requests pending...")
        if self.request_count > 275:
            logger.critical("Too many requests, exiting...")
            exit(-2)

        # Send request to SolarEdge API
        r = requests.get(url, params=params)

        # Check response code
        if r.status_code != 200:
            logger.critical(
                f"Could not get API CALL, error: {r.status_code} exiting..."
            )
            exit(-1)
        
        # Return response 
        return r


    def select_site_id(self):
        logger.debug("Querying the site_id(s)")
        
        # Call API
        r = self._api_call(f"{self.API_LINK}/sites/list", {"api_key": self.API_KEY} )
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


    def get_start_date(self):
        # Small wrapper for get_data_period
        if self.start_date is None:
            self.get_data_period()
        return parse(self.start_date)


    def get_end_date(self):
        # Small wrapper for get_data_period
        if self.end_date is None:
            self.get_data_period()
        return parse(self.end_date)


    def get_data_period(self):
        """
            Queries SolarEdge API for start and end date,
            stores these values in start_date and end_date
        """
        logger.debug("Querying dataPeriod")

        # Send request to SolarEdge API
        r = self._api_call(f"{self.API_LINK}/site/{self.SITE_ID}/dataPeriod", 
                            {"api_key": self.API_KEY})
        response = r.json()

        self.start_date = response["dataPeriod"]["startDate"]
        self.end_date = response["dataPeriod"]["endDate"]


    def get_production(self, start_date, stop_date):
        """
            Query SolarEdge API, get QUARTER_OF_AN_HOUR aggregated values from timespan
        """
        logger.debug("Querying energy data")

        # Send request to SolarEdge API
        r = self._api_call(f"{self.API_LINK}/site/{self.SITE_ID}/energy", 
                            {"api_key": self.API_KEY, 
                            "timeUnit": "QUARTER_OF_AN_HOUR",
                            "startDate": start_date.strftime("%Y-%m-%d"), 
                            "endDate": stop_date.strftime("%Y-%m-%d")})

        response = r.json()

        return response["energy"]["values"]

if __name__ == "__main__":
    print("\n\nThe solaredge_api.py is directly called, not supposed to do so...\n\n")