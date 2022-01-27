# Notities

## Diagrammen tekenen

Via [Graphviz](https://graphviz.org/Gallery/directed/datastruct.html). De `dot` file is een simpele tekstfile, met het voorbeeld is deze gemakkelijk op te bouwen. Met de achtergrondkleur wordt de voortgang van dit project weergegeven.

Van `dot` file naar `svg`: `dot -Tsvg diagram.dot -odiagram.svg`

## Solaredge API

De zonnepanelen op het dak zijn verbonden met een inverter van SolarEdge. Hier staat een en ander beschreven uit de [datasheet](documentatie/se_monitoring_api.pdf). Bron: [hier](https://www.solaredge.com/sites/default/files/se_monitoring_api.pdf) te vinden.
In de file `solaredge_api.py` wordt de interface naar Solaredge uitgewerkt. Er wordt een verbinding gemaakt met de API van Solaredge. De gevonden gegevens worden opgeslagen in een database. _Waarschijnlijk is het handiger of in ieder geval sneller om een Python-API ergens van pip of github te halen, maar dit is leerzamer._ Via `solaredge.py` wordt bepaald in welke database de gegevens komen. In deze database wordt ook het aantal _calls_ naar de API bijgehouden. Er mogen per dag maar maximaal 300 calls gemaakt worden. Voordat dit aantal bereikt wordt, geeft de `api` een foutmelding en stopt het programma. 

Korte samenvatting van de documentatie:
- Er is een API key nodig (via de installateur verkregen): `http://monitoringapi.solaredge.com/{site_id}/details.json?api_key=[your_api_key]`
- Het _siteId_ is ook nodig, kan opgezocht worden
- API link: https://monitoringapi.solaredge.com
- Respons is in JSON
- Format datum in YYYY-MM-DD
- Fair use policy: maximaal 300 calls per dag (http err 429 of 403)

URLs:

| Doel | URL | Omschrijving |
| :--- | :--- | :--- |
| Site List | /sites/list | Geeft informatie over de beschikbare sites van de API key  |
| Site Data: Start and End Dates | /site/{siteId}/dataPeriod | Return the energy production start and end dates of the site. |
| Site Energy | /site/{siteId}/energy | Return the site energy measurements \[Wh\]<br>timeUnit=HOUR<br>Maximaal 1 maand opvragen<br>Rekening houden met _null_ |
| Site Overview | /site/{siteId}/overview | Bevat de lastUpdateTime |

**Doelen en uit te voeren taken**

De volgende stappen worden genomen:
- [x] Verbinding kunnen maken met de API
- [x] Ophalen van welke _site_ de informatie beschikbaar is
- [x] Data ophalen van een maand
- [x] Data opslaan in de database
- [x] Data van overige maanden ophalen en opslaan

Optioneel:
- [x] Aantal calls per dag bijhouden, rekening houden met query-quota


## Ophalen weergegevens

De opbrengst van de zonnepanelen is afhankelijk van het weer. Welke parameters het model ingaan, zal later beschreven worden.


### Historische gegevens

Als eerste naar het KNMI gekeken. Weerstation Ell is het dichtste bij mij, voor deze opdracht ga ik er vanuit dat de gegevens aldaar representatief zijn voor het lokale weer hier. Ter info: Roermond - Ell is hemelsbreed 15 km. Een alternatief is het vliegveld in Beek (Maasticht Aachen Airport). Dit is hemelsbreed 35 km en mijns inziens daarmee ook representatief.

Het KNMI blijkt een API ter beschikking te hebben voor historische data, zie [hier](https://www.knmi.nl/kennis-en-datacentrum/achtergrond/data-ophalen-vanuit-een-script). Korte samenvatting:

- https://www.daggegevens.knmi.nl/klimatologie/uurgegevens
- Parameters:
  - start, end: YYYYMMDDHH
  - vars: ALL
  - stns: 377 (Ell)
  - fmt: json

Met Panda's `pd.DataFrame.from_dict()` is de aangeleverde JSON snel in te lezen. Daarna kan deze ook weer opgeslagen worden in een sqlite3 database met `df.to_sql`. Dit kan in principe met twee regels code, hier ga ik geen eigen functie voor schrijven. 


**Doelen en uit te voeren taken**

- [x] Ophalen data van 1 dag
- [x] Bepalen van welke dagen data op te halen. Data van de zonnepanelen is leidend.
- [x] Ophalen data meerdere dagen
- [x] Data opslaan in database


### Weersvoorspelling

Naast de historische gegevens is ook de weersvoorspelling nodig. Ook deze zal van het KNMI af komen. De voorspelling zal uit [Weer- en klimaatpluim en Expertpluim](https://www.knmi.nl/nederland-nu/weer/waarschuwingen-en-verwachtingen/weer-en-klimaatpluim) gehaald worden. Op deze website worden een aantal JSON bestanden ingelezen. Hopelijk veranderen de namen hiervan niet snel... Het ophalen van JSON is gemakkelijker dan de website te gaan scrapen.


## Database

SQLite3. Database per file. [Klik voor tutorials](https://www.sqlitetutorial.net/sqlite-python/sqlite-python-select/)



