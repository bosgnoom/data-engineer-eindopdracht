In deze [repo](https://github.com/bosgnoom/data-engineer-eindopdracht) staat de uitwerking van de eindopdracht van het NL Leert traject betreffende (Junior) Data Engineer - Bit-academy.nl. Copyright &copy; 2022 Paul Schouten.

# Eindopdracht data engineer: Voorspelling opbrengst zonnepanelen

Eind 2019 is mijn dak voorzien van zonnepanelen. Deze produceren op een zonnige dag in totaal tussen de 20 en 30kWh. Niet alle energie wordt op dat moment verbruikt. De overtollige energie stroomt terug het net in. Zonnepanelen zijn erg populair geworden, mede dankzij de subsidie erop. Door de grote hoeveelheid zonnepanelen ontstaat er op momenten een overschot aan energie op het net. 

Voorheen werd het surplus aan energie weggestreept tegen de hoeveelheid afgenomen energie, de saldeerregeling. Echter, de saldeerregeling zal vanaf 2023 langzaam afgebouwd worden. Het is mij overigens nog niet duidelijk over welke periode er beoordeeld gaat worden: Als er op jaarbasis verrekend gaat worden, zal het effect beperkt zijn. Als per dag de hoeveelheid opgewekte en verbruikte energie verrekend gaat worden, dan verandert de situatie. Op een zonnige zomerdag zullen de panelen veel meer energie produceren dan wat er verbruikt kan worden. Op een sombere winterdag zal dit andersom zijn: er zal dan meer energie verbruikt dan wat er opgewekt zal worden. Een oplossing hiervoor zou het opslaan van energie kunnen zijn. Een lange periode aan energie opslaan is geen reële situatie: per jaar wordt ongeveer 3500kWh energie verbruikt. Dan zou er (geschat) 400kWh energie opgeslagen moeten worden om door de drie donkerste maanden te komen. Een optie die wel mogelijk is, is het gebruik van een thuisaccu. De consumentenversies hebben een capaciteit tussen de 4 en 10kWh. 

Aangezien de opbrengst van zonnepanelen afhankelijk is van onder andere het weer, is bij mij de vraag ontstaan: kan op basis van een aantal parameters de opbrengst voorspeld worden? De uitkomst hiervan bepaalt hoe lang er (met een buffer van 7kWh) energie-neutraal overbrugd kan worden. De aanname hierbij is dat het verbruik van energie gemiddeld wordt per dag en dat de batterij als een ideale buffer werkt. Let op: het is evident dat er niet geheel energie-neutraal geleefd kan worden in deze maanden.

## Plan van aanpak

1. Bepalen welke parameters in het model worden meegenomen, de x-en. Hierbij wordt in eerste instantie gedacht aan: de dag van het jaar, de **hoek** en **helling** van de zon en het weer (regen, zonuren, **temperatuur**).
2. De opbrengst van de zonnepanelen wordt gemonitord. Deze data wordt al opgeslagen in een lokale influx-database. De geaggregeerde data is tevens beschikbaar in de API van [solaredge](https://www.solaredge.com/sites/default/files/se_monitoring_api.pdf). De **energie productie** zal via deze API gedownload worden.
3. Naar verwachting zullen deze gegevens vele malen ingelezen worden om het machine-learn systeem te trainen. Om deze reden zullen ze opgeslagen worden in een lokale database. Dan wordt de server van SolarEdge niet te veel belast (en kan ik aan de fair use policy voldoen).
4. Naast de opbrengst van de zonnepanelen zijn ook gegevens over het weer nodig, zowel de **historische** gegevens als de **weersvoorspelling**. Deze zullen ook in de database opgeslagen worden. De bron zal nog bepaald moeten worden. Buienradar, het **KNMI** of openweatherdata zijn potentiële bronnen.
5. De gegevens worden gevoed aan een machine-learn systeem. Er zal een model uitgezocht moeten worden. Daarnaast zal ook de nauwkeurigheid van dit model bepaald worden.
6. Voorspelling van opbrengst van de zonnepanelen voor de komende dagen wordt bepaald aan de hand van het machine-learn model.
7. Volgens het principe `in - uit + productie = accumulatie` wordt voorspeld hoe lang de accu meegaat.

Schematisch gezien:
![diagram](https://github.com/bosgnoom/data-engineer-eindopdracht/blob/main/diagram.svg)

## Uitgewerkte onderdelen

1. Ophalen historische gegevens van SolarEdge: `ophalen_solaredge.py`
2. Ophalen historische gegevens van KNMI: `ophalen_weer.py`
3. Ophalen weersvoorspelling van KNMI: `ophalen_weersvoorspelling.py` 
4. Samenvoegen historische gegevens: `build_dataset.py`
5. Data analyse en Machine learning: `Eindopdracht.ipynb`
6. Evaluatie en conclusie

