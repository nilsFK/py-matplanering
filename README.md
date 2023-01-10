# py-matplanering
py-matplantering används för att planera matschema utifrån en uppsättning av maträtter och tillhörande regler.
Reglerna appliceras på maträtterna för att skapat ett matschema.

Installation
------------
> pip install -r requirements.txt

Användning
----------
> python matplanera.py [-h] foodset ruleset output

där
* **foodset**: obligatorisk. sökvägen till filen som innehåller maträtter.
* **ruleset**: obligatorisk. sökvägen till filen som innehåller regler.
* **output**: obligatorisk. sökvägen till filen som innehåller det producerade matschemat.

För ytterligare instruktioner, kör:

> python matplanera.py -h

Exempel
-------
> python matplanera.py foodset.json ruleset.json

Projektstatus
-------------
* TODO: exempel på input (foodset, ruleset) och output.

Stöd
----
Testas regelbundet för Python 3.3.x
