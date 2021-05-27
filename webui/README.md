WebUI
=====

This directory is the source for the web front end for the Distant Reader. It is implemented as
a Python Flask application.

## Relationship to the Compute Code

The webui runs as a Gunicorn server. Its directory on the server is `/opt/reader`.
The process runs via the [runit](http://smarden.org/runit/index.html) supervisor.

The webui communicates with the compute code via three channels:

* New jobs are queued in the `TODO_PATH` directory. A new job is specisified via a TSV file with pre-defined columns.
* Finished carrels are in either the "public" carrel path or in a "private" path. Private carrels are only visible to the user who submitted them. For public and private the webui access the files directly to serve them out.
* User information, such as email addresses, are stored in the patron database. The webui also has a background process that caches carrel information into this database as well.

## Routes

The routes were mostly inherited.

| What                     | Route                                     |
|--------------------------|-------------------------------------------|
| Homepage                 | `GET /`                                   |
| About                    | `GET /about")                             |
| Acknowledgments          | `GET /acknowledgments`                    |
| Contact Us               | `GET /contact`                            |
| FAQ                      | `GET /faq`                                |
| Getting Started          | `GET /getting-started`                    |
| Gutenberg Search         | `GET /gutenberg`                          |
| CORD Search              | `GET /cord`                               |
| Create Biorxiv Carrel    | `GET,POST /create/biorxiv2carrel`         |
| Create CORD Carrel       | `GET,POST /create/cord`                   |
| Create File Carrel       | `GET,POST /create/file2carrel`            |
| Create Gutenberg Carrel  | `GET,POST /create/gutenberg`              |
| Create HathiTrust Carrel | `GET,POST /create/trust2carrel`           |
| Create URL Carrel        | `GET,POST /create/url2carrel`             |
| Create URL List Carrel   | `GET,POST /create/urls2carrel`            |
| Create ZIP Carrel        | `GET,POST /create/zip2carrel`             |
| Sign In                  | `GET,POST /login`                         |
| Oauth Callback           | `POST /login/callback`                    |
| New Account Page         | `GET,POST /login/new-orcid`               |
| Verify Account Email     | `GET /login/verify_email/<token>`         |
| Sign Out                 | `GET /logout`                             |
| Private Carrel Listing   | `GET /patrons/<username>/`                |
| Private Carrel Files     | `GET /patrons/<username>/<carrel>/<path>` |
| Delete Study Carrel      | `GET /delete/<carrel>`                    |
| Profile Page             | `GET /profile`                            |


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
