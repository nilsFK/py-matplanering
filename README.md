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

Debug
-----

Skapa en global config-fil.

> sudo cp py-matplanering/config/global_config.ini.template py-matplanering/config/global_config.ini

Exempel
-------
> python planera.py samples/sample1/config/sample_config.ini

Stöd
----
Testas regelbundet för Python 3.7.x+
