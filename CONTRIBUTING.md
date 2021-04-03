# Contributing

The Distant Reader consists of two general parts: a text processing workflow designed to run on HPC clusters, and a web-based user interface.
The parts communicate through a shared-file space containing _study carrels_.
A study carrel collects a specific pile of documents with its analysis, and
each study carrel takes the form of a directory.

## Web Interface

You can run the web interface locally with Docker.
(However, note that Docker isn't used for the production deploy).

    make web-run
    
And then you can view the website at http://localhost:8000


### Developing on the Web Interface

The web interface uses Python Flask web framework. You can run it using
the docker command, as given above. If you are changing or extending it
you might prefer to also run it locally on your computer. To do that
first install Python 3. Then install `pipenv`

    $ pip install pipenv
    $ cd webui
    $ pipenv install
    $ pipenv shell
    $ env READER_CONFIG=config.local FLASK_ENV=development FLASK_APP=main.py flask run

and the web app will be on `localhost:5000`.
    
