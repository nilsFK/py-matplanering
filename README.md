# py-matplanering
py-matplantering används för att planera scheman utifrån en uppsättning av händelser (events) och tillhörande regler (ruleset). Varje händelse kan referera till en eller flera regler för att skapa en begränsning (boundary).
Reglerna appliceras på händelserna för att skapat ett schema.

Installation
------------
> pip install -r requirements.txt

Användning
----------
> python matplanera.py [-h] <event path> <ruleset path> <output path>

där
* **event path**: obligatorisk. sökvägen till filen som innehåller händelser.
* **ruleset path**: obligatorisk. sökvägen till filen som innehåller regler.
* **output path**: obligatorisk. sökvägen till filen som innehåller det producerade schemat.

För ytterligare instruktioner, kör:

> python matplanera.py -h

Exempel
-------
> python matplanera.py
>   samples/sample1/sample1_tagged_data.json
>   samples/sample1/sample1/sample1_ruleset.json
>   samples/sample1/sample_output.json

Projektstatus
-------------
* Event input - OK
* PlannerRandomizer implementation - OK
* PlannerEugene implementation - TODO
* Schedule input - TODO

Stöd
----
Testas regelbundet för Python 3.5.x+
