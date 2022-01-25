# Notities

## Diagrammen tekenen

Via [Graphviz](https://graphviz.org/Gallery/directed/datastruct.html). De `dot` file is een simpele tekstfile, met het voorbeeld is deze gemakkelijk op te bouwen.

Van `dot` file naar `svg`: `dot -Tsvg diagram.dot -odiagram.svg`

## Solaredge API

De zonnepanelen op het dak zijn verbonden met een inverter van SolarEdge. Hier staat een en ander beschreven uit de [datasheet](documentatie/se_monitoring_api.pdf).
In deze file wordt de interface naar Solaredge uitgewerkt. De bedoeling is om een verbinding te maken met de API van Solaredge. De gevonden gegevens worden verwerkt in een Pandas DataFrame en daarna opgeslagen in een database. En ja... Waarschijnlijk is het handiger of in ieder geval sneller om een Python-API ergens van pip of github te halen, maar dit is leerzamer...

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

## Doelen en uit te voeren taken

De volgende stappen worden genomen:
- [x] Verbinding kunnen maken met de API
- [x] Ophalen van welke _site_ de informatie beschikbaar is
- [ ] Data ophalen van een maand
- [ ] Data opslaan in de database
- [ ] Data van overige maanden ophalen en opslaan

Optioneel:
- [ ] Aantal calls per dag bijhouden, rekening houden met query-quota

