#!/usr/bin/python3

"""
    Fetch weather forecast
    Source: KNMI
"""

import requests
import pandas as pd
import coloredlogs, logging
import sqlite3


# Start logger
logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s")


def ophalen_temperatuur():
    # Temperatuur ophalen van KNMI
    logger.debug("Ophalen temperatuur")

    url = 'https://cdn.knmi.nl/knmi/json/page/weer/waarschuwingen_verwachtingen/ensemble/iPluim/380_Expert_99999.json'
    r = requests.get(url)

    # Selecteer de serie "Hoge resolutie" uit alle aangeleverde gegevens
    for serie in r.json()["series"]:
        if "name" in serie.keys() and serie["name"] == "Hoge resolutie":
            temperatuur = pd.DataFrame(serie["data"], columns=["time", "temperatuur"])

    # Omzetten van unix timestamp [ms] naar datetime
    temperatuur["Tijdstip"] = pd.to_datetime(temperatuur["time"], unit="ms")

    # Tijdstippen als index gebruiken
    temperatuur.set_index("Tijdstip", inplace=True)
    temperatuur.drop("time", inplace=True, axis=1)

    return temperatuur


def ophalen_neerslag():
    ## Neerslag
    logger.debug("Ophalen neerslag")
    url = 'https://cdn.knmi.nl/knmi/json/page/weer/waarschuwingen_verwachtingen/ensemble/iPluim/380_Expert_13021.json'
    r = requests.get(url)
    import pprint
    for serie in r.json()["series"]:
        if "name" in serie.keys() and serie["name"] == "Hoge resolutie":
            neerslag = pd.DataFrame(serie["data"], columns=["time", "neerslag"])
            
    # Omzetten van unix timestamp [ms] naar datetime
    neerslag["Tijdstip"] = pd.to_datetime(neerslag["time"], unit="ms")

    # Tijdstippen naar index
    neerslag.set_index("Tijdstip", inplace=True)
    neerslag.drop("time", inplace=True, axis=1)

    return neerslag


def ophalen_bewolking():
    ## Bewolking
    logger.debug("Ophalen bewolking")
    url = 'https://cdn.knmi.nl/knmi/json/page/weer/waarschuwingen_verwachtingen/ensemble/iPluim/380_Expert_20010.json'
    r = requests.get(url)

    # Bewolking wordt anders teruggegeven, meerdere kolommen
    for serie in r.json()["series"]:
        if serie["name"] == "Onbewolkt": 
            onbewolkt = pd.DataFrame(serie["data"], columns=["time", "onbewolkt"])
        if serie["name"] == "Licht bewolkt": 
            licht_bewolkt = pd.DataFrame(serie["data"], columns=["time", "licht_bewolkt"])
        if serie["name"] == "Half bewolkt": 
            half_bewolkt = pd.DataFrame(serie["data"], columns=["time", "half_bewolkt"])
        if serie["name"] == "Zwaar bewolkt": 
            zwaar_bewolkt = pd.DataFrame(serie["data"], columns=["time", "zwaar_bewolkt"])
        if serie["name"] == "Geheel bewolkt": 
            geheel_bewolkt = pd.DataFrame(serie["data"], columns=["time", "geheel_bewolkt"])

    # Alle typen bewolking in één dataframe stoppen    
    # Stap voor stap mergen van kolommen    
    bewolking = onbewolkt.merge(licht_bewolkt, on="time")
    bewolking = bewolking.merge(half_bewolkt, on="time")
    bewolking = bewolking.merge(zwaar_bewolkt, on="time")
    bewolking = bewolking.merge(geheel_bewolkt, on="time")

    # Controle uitvoeren, som = 100%
    # --> Ja klopt, ter referentie hier laten staan
    #bewolking["controle"] = bewolking["onbewolkt"] + bewolking["licht_bewolkt"] + bewolking["half_bewolkt"] + bewolking["zwaar_bewolkt"] + bewolking["geheel_bewolkt"]

    # Omzetten timestamp naar tijd (index)
    bewolking["Tijdstip"] = pd.to_datetime(bewolking["time"], unit="ms")
    bewolking.set_index("Tijdstip", inplace=True)
    bewolking.drop("time", inplace=True, axis=1)

    # Bewolking score uitrekenen
    # Nul keer iets is altijd nul, maar voor leesbaarheid laten staan
    bewolking["bewolking"] = (0 * bewolking["onbewolkt"] + 
                                2 * bewolking["licht_bewolkt"] + 
                                4 * bewolking["half_bewolkt"] + 
                                6 * bewolking["zwaar_bewolkt"] + 
                                8 * bewolking["geheel_bewolkt"])/100

    return bewolking


def get_data():
    ## Combineren van de weersvoorspelling
    logger.info("Ophalen weersvoorspelling")
    temperatuur = ophalen_temperatuur()
    neerslag = ophalen_neerslag()
    bewolking = ophalen_bewolking()

    # De temperatuur, neerslag en bewolking worden in één dataframe opgeslagen
    logger.info("Weersvoorspelling samenvoegen")
    voorspelling = temperatuur.merge(neerslag, left_index=True, right_index=True)
    voorspelling = voorspelling.merge(bewolking["bewolking"], left_index=True, right_index=True)

    # Voorspelling opslaan in een SQLite3 database
    logger.info("Weersvoorspelling opslaan in de database")
    conn = sqlite3.connect("voorspelling.db")
    cursor = conn.cursor()

    # Vorige voorspelling wissen
    cursor.execute("DROP TABLE IF EXISTS voorspelling")

    # Voorspelling opslaan in database
    voorspelling.to_sql("voorspelling", conn)

    # Opslaan en afsluiten
    conn.commit()
    conn.close()


# Wrap get_data into __main__, so this function can be
# called through an "import ophalen_weersvoorspelling"
if __name__ == "__main__":
    get_data()
