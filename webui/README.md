WebUI
=====

This directory is the source for the web front end for the Distant Reader. It is implemented as
a Python Flask application.


## How-Tos

### Run the app locally

```
pipenv shell
env READER_CONFIG=config.local FLASK_ENV=development FLASK_APP=main.py flask run
```

### Create a database migration

```
yoyo new ./migrations --sql -m "Add carrel table"
```
