#!/usr/bin/python3


"""
    Combine data from solaredge and historical weather into one dataset
"""


import sqlite3
import pysolar
import pandas as pd
import coloredlogs, logging

import ophalen_solaredge
import ophalen_weer
import ophalen_weersvoorspelling


# Start logger
logger = logging.getLogger(__name__)
coloredlogs.install(level="INFO", fmt="%(asctime)s %(levelname)s %(message)s")


# Inlezen gegevens solaredge
def inlezen_solaredge(conn):
    logger.debug("Inlezen gegevens SolarEdge")

    # Database inlezen
    data = pd.read_sql("SELECT * FROM solaredge_history", conn)

    # Tijd omzetten naar datetime
    data["Time"] = pd.to_datetime(data["tijdstip"])
    data.set_index("Time", inplace=True)
    data.drop("tijdstip", axis=1, inplace=True)

    # Tijdzone info toevoegen, SolarEdge is in de "local" time
    data = data.tz_localize("Europe/Amsterdam", ambiguous="NaT", nonexistent="NaT")

    return data


# Inlezen gegevens weer
def inlezen_weer(conn):
    logger.debug("Inlezen gegevens weer")

    # Database inlezen
    data = pd.read_sql("SELECT * FROM knmi_history", conn)

    # Date en hour omzetten naar datetime
    data["Time"] = pd.to_datetime(data["date"]) + pd.TimedeltaIndex(
        data["hour"], unit="h"
    )

    data.set_index("Time", inplace=True)
    data.drop(["date", "hour", "id", "station_code"], inplace=True, axis=1)

    # De temperatuur staat in 0.1°C, deze wordt nu door 10 gedeeld om de
    # goede temperatuur te krijgen
    data["T"] = data["T"] / 10

    return data


def combine_data():
    # Open database
    conn = sqlite3.connect("database.db")

    # Zonnepanelen worden per kwartier gesampled. Met _resample_ het totaal per uur uitrekenen
    logger.info("Inlezen SolarEdge, resample naar 1H interval")
    zonnepanelen = inlezen_solaredge(conn).resample("1H").sum()

    # Data van het weer inlezen. Samenvoegen met data zonnepanelen
    logger.info("Inlezen weer, samenvoegen met SolarEdge")
    data = inlezen_weer(conn)
    data = data.merge(zonnepanelen, left_index=True, right_index=True)

    # Nu ook de positie van de zon berekenen op basis van mijn positie
    # TODO: set location from config.ini
    logger.info("Positie van de zon uitrekenen")
    latitude = 51.2
    longitude = 6

    logger.debug("Solar altitude")
    data["alt"] = pysolar.solar.get_altitude_fast(latitude, longitude, data.index)

    logger.debug("Solar azimuth")
    data["azi"] = pysolar.solar.get_azimuth_fast(latitude, longitude, data.index)

    # Kolommen een begrijpelijke naam geven
    logger.info("Kolommen andere naam geven")
    data.rename(
        columns={
            "T": "temperatuur",
            "DR": "duur_neerslag",
            "N": "bewolking",
            "alt": "solar_altitude",
            "azi": "solar_azimuth",
        },
        inplace=True,
    )

    # Dataset opslaan voor te gebruiken in machine learn model
    logger.info("Dataset opslaan")
    data_export = data[
        [
            "temperatuur",
            "duur_neerslag",
            "bewolking",
            "solar_altitude",
            "solar_azimuth",
            "energy",
        ]
    ]
    data_export.to_sql("dataset", con=conn, if_exists="replace")

    conn.commit()
    conn.close()


def fetch_data():
    logger.info("Fetching data from SolarEdge")
    ophalen_solaredge.get_data()

    logger.info("Fetching weather history from KNMI")
    ophalen_weer.get_data()

    logger.info("Fetching weather forecast from KNMI")
    ophalen_weersvoorspelling.get_data()


if __name__ == "__main__":
    fetch_data()
    combine_data()
