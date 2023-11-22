# Manifest Library Sync Service

De Manifest Library Sync Service is verantwoordelijk voor het ophalen van
[IIIF-manifesten](https://iiif.io/api/presentation/3.0/) vanuit verschillende
bronnen en deze op te slaan in de [elody collection-api](https://github.com/inuits/elody-collection).

## Bronnen

Er zijn momenteel twee typen bronnen mogelijk:
* [IIIF-Collection-importer](https://iiif.io/api/presentation/3.0/#51-collection)
* OAI-PMH importer

De IIIF-Collection-importer gebruikt een IIIF Collection, onderdeel van de [IIIF-presentation-standaard](https://iiif.io/api/presentation/3.0/#51-collection),
om manifesten op te halen.

De OAI-PMH importer gebruikt de [OAI-PMH](https://www.openarchives.org/pmh/)
standaard om manifesten op te halen.

Binnen deze twee typen van bronnen zijn nog specifieke uitbreidingen. Niet alle
manifesten zijn namelijk op dezelfde manier gestructureerd. Sommige manifesten
hebben ook metadata staan in een extern bronbeheersysteem, zoals [LIDO](https://cidoc.mini.icom.museum/working-groups/lido/lido-overview/about-lido/what-is-lido/).
Hiervoor is een specifieke implementatie om na het ophalen van het manifest ook
de metadata uit dit bronsysteem op te halen en deze toe te voegen aan de
manifestenbibliotheek.

Programmatisch is het mogelijk gemaakt om relatief eenvoudig een bron toe te
voegen. Dit door een [Python class](https://docs.python.org/3/tutorial/classes.html)
te maken die overerft van de "[Base Importer](https://github.com/VlaamseKunstcollectie/IIIF-Manifest-Library-importer/blob/master/importers/base_importer.py)"-
class.

## Sync uitvoeren

Deze service is eenvoudig uit te voeren via de [Python Interpreter](https://docs.python.org/3/tutorial/interpreter.html).
De configuratie, bestaande uit URL's naar de verschillende bronnen, wordt
doorgegeven aan de hand van "environment variables". De dependencies van de
service zijn opgelijst in de [requirements.txt](https://github.com/VlaamseKunstcollectie/IIIF-Manifest-Library-importer/blob/master/requirements.txt)-file.

Voorbeeld uitvoering script:
``` bash
# (optioneel: aanmaken van een Python virtual env)
python3 -m venv .
source ./bin/activate
# Installeren van dependencies
pip install -r requirements.txt
# Uitvoeren van het script
export ELODY_COLLECTION_URL=<URL naar elody collection-api>
export LIDO_URLS=https://datahub.vlaamsekunstcollectie.be/oai/
export STATIC_JWT=<JWT token om de collection-api te bereiken>
export COLLECTION_URLS_OBB=https://sharedcanvas.be/IIIF/mmmonk/discover
export COLLECTION_URLS=https://imagehub.vlaamsekunstcollectie.be/iiif/3/collection/top
export MPM_OAI_URLS=https://dams.antwerpen.be/oai/request
python main.py
```
