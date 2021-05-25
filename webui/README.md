WebUI
=====

This directory is the source for the web front end for the Distant Reader. It is implemented as
a Python Flask application.


## How-Tos

### Run the app locally

* The app uses Python 3. Install that on your computer. (On my mac I use Homebrew: `brew install python3`)
* Install the `pipenv` package: `pip3 install pipenv`
* Go to the `webui` directory: `cd webui`
* Ask pipenv to install all the other needed packages: `pipenv sync`
  * If you get an error similar to "cannot find python3.6" run `pipenv --python=/usr/local/bin/python3` and then do `pipenv sync`
  * If you get a warning that your version of python is newer than 3.6, don't worry about it.
* Enter a shell that uses these packages: `pipenv shell`
* Setup the environment variables (this is for bash, probably what you will want unless you know otherwise):
  * `export READER_CONFIG=config.local FLASK_ENV=development FLASK_APP=main.py`
* Start the flask server: `flask run`
* The site can be viewed at http://localhost:5000/


```
pipenv shell
env READER_CONFIG=config.local FLASK_ENV=development FLASK_APP=main.py flask run
```

### Create a database migration

```
yoyo new ./migrations --sql -m "Add carrel table"
```
