# py-matplanering
================
py-matplantering används för att planera matschema utifrån en uppsättning av maträtter och tillhörande regler.

Installation
------------
> pip install -r requirements.txt

Användning
----------
> python matplanera.py [-h] foodset ruleset

där
* **foodset**: obligatorisk. sökvägen till filen som innehåller maträtter.
* **ruleset**: obligatorisk. sökvägen till filen som innehåller regler.

För ytterligare instruktioner, kör:

> python matplanera.py -h

Exempel
-------
> python matplanera.py foodset.json ruleset.json

Projektstatus
-------------
* Pågående...

Stöd
----
Testas regelbundet för Python 3.3.x
