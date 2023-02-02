# py-matplanering
py-matplantering används för att planera scheman utifrån en uppsättning av händelser (events) och tillhörande regler (ruleset). Varje händelse kan referera till en eller flera regler för att skapa en begränsning (boundary).
Reglerna appliceras på händelserna för att skapa ett schema.

Installation
------------
> pip install -r requirements.txt

Användning
----------
> python planera.py [-h] path/to/config.ini

För ytterligare instruktioner, kör:

> python planera.py -h

Exempel
-------
> python planera.py samples/sample1/config/sample_config.ini

Projektstatus
-------------
* Event input - OK
* PlannerRandomizer implementation - OK
* PlannerEugene implementation - TODO
* Schedule input - TODO

Stöd
----
Testas regelbundet för Python 3.5.x+
