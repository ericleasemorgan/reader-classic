from datetime import datetime
import secrets
import os.path
from flask import render_template, session, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, current_user
from is_safe_url import is_safe_url
import pysolr

from app import app
from auth import oauth
from models import User, EmailToken


@app.route("/")
def index():
    return render_template("home.html")

@app.errorhandler(404)
def page_not_found(error):
    return (render_template("404.html"), 404)

@app.errorhandler(500)
def server_error(error):
    return (render_template("500.html"), 500)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        redirect_uri = url_for("login_callback", _external=True)
        return oauth.orcid.authorize_redirect(redirect_uri, scope="/authenticate")
    return render_template("login.html")


@app.route("/login/callback", methods=["GET", "POST"])
def login_callback():
    """this is the oauth callback"""
    token = oauth.orcid.authorize_access_token()
    # Is there an existing user for this orcid?
    orcid = token["orcid"]
    u = User.FromORCID(orcid)
    if u is not None:
        # YES, there is a record with this orcid
        login_user(u)
        next = session.pop("next", url_for("index"))
        if not is_safe_url(next, allowed_hosts=None):
            next = url_for("index")
        return redirect(next)
    # save the important token info and ask if we should consolidate with
    # existing account or make a new one
    session["orcid"] = orcid
    session["name"] = token["name"]
    return redirect(url_for("login_new_orcid"))


# pulls info out of the current request. looks for form fields
# `username`, `email`. Returns None and sets the flash if there was a
# validation error.
def populate_user_from_form():
    username = request.form.get("username", "")
    if username == "":
        flash("A username is required")
        return None
    if User.FromUsername(username) is not None:
        flash("Please choose a username not already used")
        return None
    email = request.form.get("email", "")
    if email == "":
        flash("An email is required")
        return None
    return User(username=username, email=email)


@app.route("/login/new-orcid", methods=["GET", "POST"])
def login_new_orcid():
    # the user has logged in with ORCID, but there is not a record with that
    # ORCID, so ask user information to create a new one.
    #
    # The user is not technically logged in at this point (because there is no
    # user id yet!). We are storing the given orcid and name in the session.
    if request.method == "GET":
        return render_template("login-new-orcid.html")
    # make a new account
    # is username taken?
    u = populate_user_from_form()
    if u is None:
        return render_template("login-new-orcid.html")
    u.name = request.form.get("name", session.pop("name"))
    u.orcid = session.pop("orcid")
    u.save()

    send_email_verification(u)

    login_user(u)
    next = session.pop("next", url_for("index"))
    if not is_safe_url(next, allowed_hosts=None):
        next = url_for(index)
    return redirect(next)

@app.route("/login/verify_email/<token>")
def verify_email(token):
    ev = EmailToken.FromToken(token)
    if ev is None:
        flash("Can't verify email: unknown token")
        return redirect(url_for("index"))
    u = User.FromID(ev.userid)
    if u is None:
        flash("Can't verify email: unknown user")
        return redirect(url_for("index"))
    if u.email_verify_date != "":
        # the user already has a verified email
        flash("Email Verified")
        return redirect(url_for("index"))
    if u.email != ev.email:
        # the token was issued for an old email address
        flash("Can't verify email: old token")
        return redirect(url_for("index"))
    u.email_verify_date = datetime.today()
    u.save()
    ev.delete()
    flash("Email Verified")
    return redirect(url_for("index"))

def send_email_verification(user):
    assert user is not None
    if user.email_verify_date != "":
        return
    if user.email == "":
        return
    token = secrets.token_urlsafe()
    ev = EmailToken(token=token, email=user.email, userid=user.id)
    ev.save()

    # now send email
    body = render_template("verify-email.txt", token=token)
    send_email(to=user.email, subject="Email Verification", body=body)



# these routes are only for development testing of the oauth login
if app.debug:
    import base64

    @app.route("/oauth/authorize", methods=["GET", "POST"])
    def debug_oauth_authorize():
        print(request.args)
        if request.method == "GET":
            return render_template("debug-oauth-authorize.html")
        # we put the data we want to remember into the session
        # base64 works on _bytes_ but we have _strings_ so lots of encoding/decoding needed
        code = "{}:{}".format(request.form["name"], request.form["orcid"]).encode(
            "utf-8"
        )
        codestr = base64.b64encode(code).decode("utf-8")
        return redirect(
            "{}?code={}&state={}".format(
                request.form["redirect"], codestr, request.form["state"]
            )
        )

    @app.route("/oauth/token", methods=["POST"])
    def debug_oauth_token():
        print(request.args)
        print(request.form)
        x = base64.b64decode(request.form["code"].encode("utf-8"))
        name, orcid = x.decode("utf-8").split(":", 1)
        return {
            "access_token": "debugging-token",
            "token_type": "bearer",
            "refresh_token": "refresh-debugging-token",
            "expires_in": 631138518,
            "scope": "/authenticate",
            "name": name,
            "orcid": orcid,
            "expires_at": 2248258384,
        }


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


def add_job_to_queue(job_type, shortname, username, extra):
    now = datetime.now().strftime("%Y-%m-%d\t%H:%M")
    # since shortname is user supplied, different users many use the same name
    shortname = secure_filename(shortname)
    with open(os.path.join(app.config["TODO_PATH"], shortname + ".tsv"), mode="w") as f:
        f.write("\t".join([job_type, shortname, now, username, extra]))
        f.write("\n")


@app.route("/create/url2carrel", methods=["GET", "POST"])
@login_required
def url2carrel():
    TYPE = "url2carrel"
    shortname = request.form.get("shortname", "")
    target_url = request.form.get("url", "")
    username = current_user.username

    if request.method != "POST" or shortname == "" or target_url == "":
        return render_template("url2carrel.html")
    shortname = secure_filename(shortname)
    add_job_to_queue(TYPE, shortname, username, target_url)
    return render_template(
        "urls2carrel-queue.html", username=username, shortname=shortname
    )


@app.route("/create/urls2carrel", methods=["GET", "POST"])
@login_required
def urls2carrel():
    TYPE = "urls2carrel"

    # initialize
    shortname = request.form.get("shortname", "")
    username = current_user.username

    if request.method != "POST" or shortname == "":
        return render_template("urls2carrel.html")
    shortname = secure_filename(shortname)
    # get the basename of the loaded file, and move it to the backlog
    f = request.files["file"]
    name = secure_filename(f.filename)
    f.save(os.path.join(app.config["BACKLOG_PATH"], name))

    add_job_to_queue(TYPE, shortname, username, name)
    return render_template(
        "urls2carrel-queue.html", username=username, shortname=shortname
    )


@app.route("/create/zip2carrel", methods=["GET", "POST"])
@login_required
def zip2carrel():
    TYPE = "zip2carrel"

    # initialize
    shortname = request.form.get("shortname", "")
    username = current_user.username

    if request.method != "POST" or shortname == "":
        return render_template("zip2carrel.html")
    shortname = secure_filename(shortname)
    # get the basename of the loaded file, and move it to the backlog
    f = request.files["file"]
    name = secure_filename(f.filename)
    f.save(os.path.join(app.config["BACKLOG_PATH"], name))

    add_job_to_queue(TYPE, shortname, username, name)
    return render_template(
        "zip2carrel-queue.html", username=username, shortname=shortname
    )


@app.route("/create/file2carrel", methods=["GET", "POST"])
@login_required
def file2carrel():
    TYPE = "file2carrel"

    shortname = request.form.get("shortname", "")
    username = current_user.username

    if request.method != "POST" or shortname == "":
        return render_template("file2carrel.html")
    shortname = secure_filename(shortname)
    # get the basename of the loaded file, and move it to the backlog
    f = request.files["file"]
    name = secure_filename(f.filename)
    f.save(os.path.join(app.config["BACKLOG_PATH"], name))

    add_job_to_queue(TYPE, shortname, username, name)
    return render_template(
        "file2carrel-queue.html", username=username, shortname=shortname
    )


@app.route("/create/trust2carrel", methods=["GET", "POST"])
@login_required
def trust2carrel():
    TYPE = "trust"

    # initialize
    shortname = request.form.get("shortname", "")
    username = current_user.username

    if request.method != "POST" or shortname == "":
        return render_template("trust2carrel.html")
    shortname = secure_filename(shortname)
    # get the basename of the loaded file, and move it to the backlog
    f = request.files["file"]
    name = secure_filename(f.filename)
    f.save(os.path.join(app.config["BACKLOG_PATH"], name))

    add_job_to_queue(TYPE, shortname, username, name)
    return render_template(
        "trust2carrel-queue.html", username=username, shortname=shortname
    )


@app.route("/create/biorxiv2carrel", methods=["GET", "POST"])
@login_required
def biorxiv2carrel():
    TYPE = "biorxiv"

    shortname = request.form.get("shortname", "")
    username = current_user.username

    if request.method != "POST" or shortname == "":
        return render_template("biorxiv2carrel.html")
    shortname = secure_filename(shortname)
    # get the basename of the loaded file, and move it to the backlog
    f = request.files["file"]
    name = secure_filename(f.filename)
    f.save(os.path.join(app.config["BACKLOG_PATH"], name))

    add_job_to_queue(TYPE, shortname, username, name)
    return render_template(
        "biorxiv2carrel-queue.html", username=username, shortname=shortname
    )


# list_to_pairs takes a list like ['aaa', 123, 'bbb', 234, 'ccc', 345, ...]
# interprets it as a list of key-value pairs, and returns
# the list of those pairs e.g. [('aaa', 123), ('bbb', 234), ('ccc', 345), ...]
def list_to_pairs(a):
    i = iter(a)
    return list(zip(i, i))


# keep_non_zero takes a list of pairs [(a,b), (c,d), ...] and returns a list
# of pairs where the second element is > 0
def keep_positive(a):
    return [(x, y) for x, y in a if y > 0]


@app.route("/gutenberg")
def gutenberg():
    # configure
    FACETFIELD = ["facet_subject", "facet_author", "facet_classification"]
    ROWS = 499

    # initialize
    query = request.args.get("query", "")
    solr = pysolr.Solr(url=app.config["SOLR_URL_GUTENBERG"])

    if query == "":
        return render_template("gutenberg.html", query="", results=[])

    # build the search options
    search_options = {"facet.field": FACETFIELD, "facet": "true", "rows": ROWS}

    response = solr.search(query, **search_options)

    facets = {
        facet: keep_positive(list_to_pairs(v))
        for facet, v in response.facets["facet_fields"].items()
    }

    total_hits = response.hits
    num_displayed = len(response)

    # sort the subject and classification field for these results
    for doc in response.docs:
        doc.get("classification", []).sort()
        doc.get("subject", []).sort()

    return render_template(
        "gutenberg-results.html",
        query=query,
        total_hits=total_hits,
        num_displayed=num_displayed,
        results=response.docs,
        facets=facets,
    )


@app.route("/create/gutenberg", methods=["GET", "POST"])
@login_required
def create_gutenberg():
    TYPE = "gutenberg"

    # initialize
    # query is passed as a param for GET requests and as
    # as a form vaule for POSTs.
    shortname = request.form.get("shortname", "")
    username = current_user.username

    if request.method != "POST" or shortname == "":
        query = request.args.get("query", "")
        return render_template("gutenberg-create.html", query=query)

    query = request.form.get("query", "")
    shortname = secure_filename(shortname)
    add_job_to_queue(TYPE, shortname, username, query)
    return render_template(
        "gutenberg-queue.html", username=username, shortname=shortname
    )


@app.route("/cord")
def cord_search():
    FACETFIELD = [
        "facet_journal",
        "year",
        "facet_authors",
        "facet_keywords",
        "facet_entity",
        "facet_type",
        "facet_sources",
    ]
    FIELDS = "id,title,doi,urls,date,journal,abstract,sources,pmc_json,pdf_json,sha"
    ROWS = 49

    # initialize
    query = request.args.get("query", "")
    solr = pysolr.Solr(url=app.config["SOLR_URL_CORD"])

    # display the home page
    if query == "":
        return render_template("cord.html", query="", results=[])

    # build the search options
    search_options = {
        "facet.field": FACETFIELD,
        "fl": FIELDS,
        "facet": "true",
        "rows": ROWS,
    }

    response = solr.search(query, **search_options)

    facets = {
        facet: keep_positive(list_to_pairs(v))
        for facet, v in response.facets["facet_fields"].items()
    }
    total_hits = response.hits
    num_displayed = len(response)

    return render_template(
        "cord-results.html",
        query=query,
        total_hits=total_hits,
        num_displayed=num_displayed,
        results=response.docs,
        facets=facets,
    )


@app.route("/create/cord", methods=["GET", "POST"])
@login_required
def create_cord():
    TYPE = "cord"

    # initialize
    # query is passed as a param for GET requests and as
    # as a form vaule for POSTs.
    shortname = request.form.get("shortname", "")
    username = current_user.username

    if request.method != "POST" or shortname == "":
        query = request.args.get("query", "")
        return render_template("cord-create.html", query=query)

    query = request.form.get("query", "")
    shortname = secure_filename(shortname)
    add_job_to_queue(TYPE, shortname, username, query)
    return render_template("cord-queue.html", username=username, shortname=shortname)
