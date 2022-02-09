#!/usr/bin/python3


"""
    Combine data from solaredge and historical weather into one dataset
"""


import sqlite3
import pysolar
import pandas as pd
import coloredlogs, logging


# Start logger
logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s")


# Inlezen gegevens solaredge
def inlezen_solaredge():
    logger.debug("Inlezen gegevens SolarEdge")
    # Database inlezen
    conn = sqlite3.connect("solaredge.db")
    data = pd.read_sql('SELECT * FROM history', conn)
    
    # Tijd omzetten naar datetime
    data["Time"] = pd.to_datetime(data["tijdstip"])
    data.set_index("Time", inplace=True)
    data.drop("tijdstip", axis=1, inplace=True)
    
    # Tijdzone info toevoegen, SolarEdge is in de "local" time
    data = data.tz_localize("Europe/Amsterdam", ambiguous="NaT", nonexistent="NaT")
        
    return data


# Inlezen gegevens weer
def inlezen_weer():
    logger.debug("Inlezen gegevens weer")
    # Database inlezen
    conn = sqlite3.connect("knmi.db")
    data = pd.read_sql('SELECT * FROM knmi', conn)
    
    # Date en hour omzetten naar datetime
    data["Time"] = pd.to_datetime(data["date"]) + pd.TimedeltaIndex(data["hour"], unit='h')
    
    data.set_index("Time", inplace=True)
    data.drop(["date", "hour", "id", "station_code"], inplace=True, axis=1)

    # De temperatuur staat in 0.1°C, deze wordt nu door 10 gedeeld om de
    # goede temperatuur te krijgen
    data["T"] = data["T"] / 10
    return data


def combine_data():
    # Zonnepanelen worden per kwartier gesampled. Met _resample_ het totaal per uur uitrekenen
    logger.info("Inlezen SolarEdge, resample naar 1H interval")
    zonnepanelen = inlezen_solaredge().resample("1H").sum()
        
    # Data van het weer inlezen. Samenvoegen met data zonnepanelen
    logger.info("Inlezen weer, samenvoegen met SolarEdge")
    data = inlezen_weer()
    data = data.merge(zonnepanelen, left_index=True, right_index=True)

    # Nu ook de positie van de zon berekenen op basis van mijn positie
    logger.info("Positie van de zon uitrekenen")
    latitude = 51.2
    longitude = 6

    # pysolar heeft een datetime nodig. Met reset_index van de tijd een kolom maken,
    # berekeningen uitvoeren en de tijd kolom weer als index terugzetten
    data.reset_index(inplace=True)
    # Ik ben er nog niet achter hoe deze functies te _mappen_, dan maar via lambda
    logger.debug("Solar altitude")
    data["alt"] = data.apply(
        lambda row: pysolar.solar.get_altitude_fast(
            latitude, longitude, 
            row["Time"].to_pydatetime()), 
        axis=1)

    logger.debug("Solar azimuth")
    data["azi"] = data.apply(
        lambda row: pysolar.solar.get_azimuth(
            latitude, longitude, 
            row["Time"].to_pydatetime()),
        axis=1)
    data.set_index("Time", inplace=True)

    # Kolommen een begrijpelijke naam geven
    logger.info("Kolommen andere naam geven")
    data.rename(columns={"T": "temperatuur", 
                "DR": "duur_neerslag", 
                "N": "bewolking", 
                "alt": "solar_altitude", 
                "azi": "solar_azimuth"},
                inplace=True)

    # Dataset opslaan voor te gebruiken in machine learn model
    logger.info("Dataset opslaan")
    conn = sqlite3.connect("dataset.db")
    data_export = data[["temperatuur", "duur_neerslag", "bewolking", "solar_altitude", "solar_azimuth", "energy"]]
    data_export.to_sql('history', con=conn, if_exists='replace')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    combine_data()
