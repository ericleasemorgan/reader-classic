from datetime import datetime
import os.path
from flask import (render_template, session, request, redirect, g, url_for, flash)
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, current_user
from is_safe_url import is_safe_url
import pysolr

from app import app
from auth import login_manager, verify_password, oauth
from models import User

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # which method did the user choose: orcid or password?
        if request.form.get('which', '') == "orcid":
            redirect_uri = url_for('login_callback', _external=True)
            return oauth.orcid.authorize_redirect(redirect_uri, scope="/authenticate")
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if verify_password(username, password):
            u = User.FromUsername(username)
            if u is None:
                u = User(username=username)
                u.save()
            login_user(u)
            next = session.pop('next', url_for('index'))
            if not is_safe_url(next, allowed_hosts=None):
                next = url_for(index)
            return redirect(next)
    return render_template('login.html')

@app.route('/login/callback', methods=['GET', 'POST'])
def login_callback():
    """this is the oauth callback"""
    token = oauth.orcid.authorize_access_token()
    # Is there an existing user for this orcid?
    orcid = token['orcid']
    u = User.FromORCID(orcid)
    if u is not None:
        # YES, there is a record with this orcid
        login_user(u)
        next = session.pop('next', url_for('index'))
        if not is_safe_url(next, allowed_hosts=None):
            next = url_for('index')
        return redirect(next)
    # save the important token info and ask if we should consolidate with
    # existing account or make a new one
    session['orcid'] = orcid
    session['name'] = token['name']
    return redirect(url_for('login_new_orcid'))

# pulls info out of the current request. looks for form fields
# `username`, `email`. Returns None and sets the flash if there was a
# validation error.
def create_user_from_form():
    username = request.form.get('username', '')
    if username == '':
        flash('username is required')
        return None
    if User.FromUsername(username) is not None:
        flash('That username is used by someone else')
        return None
    email = request.form.get('email', '')
    if email == '':
        flash('An email is required')
        return None
    return User(username = username, email=email)

@app.route('/login/new-orcid', methods=['GET', 'POST'])
def login_new_orcid():
    # the user has logged in with ORCID, but there is not a record with that
    # ORCID, so ask whether to make a new one or to consolidate with an
    # existing one.
    # The user is not technically logged in yet, but we are storing the given
    # orcid and name in the session, temporarily. (to log them in we would need
    # to add a record to the database, sooooo either we figure out which record
    # right now or we make a record and then possibly delete it later if they
    # choose "associate"
    if request.method == "GET":
        return render_template('login-new-orcid.html')
    # should we add this orcid to an existing account?
    if request.form.get('which', '') == "associate":
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if not verify_password(username, password):
            flash("username and password don't match")
            return render_template('login-new-orcid.html')
        u = User.FromUsername(username)
        name = session.pop('name')
        if u is None:
            u = User(username=username)
            u.name = name
        u.orcid = session.pop('orcid')
        u.save()
    else:
        # make a new account
        # is username taken?
        u = create_user_from_form()
        if u is None:
            return render_template('login-new-orcid.html')
        u.name = session.pop('name')
        u.orcid = session.pop('orcid')
        u.save()

    login_user(u)
    next = session.pop('next', url_for('index'))
    if not is_safe_url(next, allowed_hosts=None):
        next = url_for(index)
    return redirect(next)


def add_job_to_queue(job_type, shortname, username, extra):
    now = datetime.now().strftime("%Y-%m-%d\t%H:%M")
    # since shortname is user supplied, different users many use the same name
    shortname = secure_filename(shortname)
    with open(os.path.join(app.config['TODO_PATH'], shortname + ".tsv"), mode="w") as f:
        f.write("\t".join([job_type, shortname, now, username, extra]))
        f.write("\n")

@app.route('/create/url2carrel', methods=['GET', 'POST'])
@login_required
def url2carrel():
    TYPE = 'url2carrel'
    shortname = request.form.get('shortname', '')
    target_url = request.form.get('url', '')
    username = current_user.username

    if request.method != 'POST' or shortname == '' or target_url == '':
        return render_template('url2carrel.html')
    shortname = secure_filename(shortname)
    add_job_to_queue(TYPE, shortname, username, target_url)
    return render_template('urls2carrel-queue.html', username=username, shortname=shortname)

@app.route('/create/urls2carrel', methods=['GET', 'POST'])
@login_required
def urls2carrel():
    TYPE = 'urls2carrel'

    # initialize
    shortname  = request.form.get('shortname', '')
    queue = request.form.get('queue', '')
    username = current_user.username

    if request.method != 'POST' or shortname == '':
        return render_template('urls2carrel.html')
    shortname = secure_filename(shortname)
    # get the basename of the loaded file, and move it to the backlog
    f = request.files['file']
    name = secure_filename(f.filename)
    f.save(os.path.join(app.config['BACKLOG_PATH'], name))

    add_job_to_queue(TYPE, shortname, username, name)
    return render_template('urls2carrel-queue.html', username=username, shortname=shortname)


@app.route('/create/zip2carrel', methods=['GET', 'POST'])
@login_required
def zip2carrel():
    TYPE = 'zip2carrel'

    # initialize
    shortname = request.form.get('shortname', '')
    queue = request.form.get('queue', '')
    username = current_user.username

    if request.method != 'POST' or shortname == '':
        return render_template('zip2carrel.html')
    shortname = secure_filename(shortname)
    # get the basename of the loaded file, and move it to the backlog
    f = request.files['file']
    name = secure_filename(f.filename)
    f.save(os.path.join(app.config['BACKLOG_PATH'], name))

    add_job_to_queue(TYPE, shortname, username, name)
    return render_template('zip2carrel-queue.html', username=username, shortname=shortname)

@app.route('/create/file2carrel', methods=['GET', 'POST'])
@login_required
def file2carrel():
    TYPE = 'file2carrel'

    shortname = request.form.get('shortname', '')
    queue = request.form.get('queue', '')
    username = current_user.username

    if request.method != 'POST' or shortname == '':
        return render_template('file2carrel.html')
    shortname = secure_filename(shortname)
    # get the basename of the loaded file, and move it to the backlog
    f = request.files['file']
    name = secure_filename(f.filename)
    f.save(os.path.join(app.config['BACKLOG_PATH'], name))

    add_job_to_queue(TYPE, shortname, username, name)
    return render_template('file2carrel-queue.html', username=username, shortname=shortname)

@app.route('/create/trust2carrel', methods=['GET', 'POST'])
@login_required
def trust2carrel():
    TYPE = 'trust'

    # initialize
    shortname = request.form.get('shortname', '')
    queue = request.form.get('queue', '')
    username = current_user.username

    if request.method != 'POST' or shortname == '':
        return render_template('trust2carrel.html')
    shortname = secure_filename(shortname)
    # get the basename of the loaded file, and move it to the backlog
    f = request.files['file']
    name = secure_filename(f.filename)
    f.save(os.path.join(app.config['BACKLOG_PATH'], name))

    add_job_to_queue(TYPE, shortname, username, name)
    return render_template('trust2carrel-queue.html', username=username, shortname=shortname)

@app.route('/create/biorxiv2carrel', methods=['GET', 'POST'])
@login_required
def biorxiv2carrel():
    TYPE = 'biorxiv'

    shortname = request.form.get('shortname', '')
    queue = request.form.get('queue', '')
    username = current_user.username

    if request.method != 'POST' or shortname == '':
        return render_template('biorxiv2carrel.html')
    shortname = secure_filename(shortname)
    # get the basename of the loaded file, and move it to the backlog
    f = request.files['file']
    name = secure_filename(f.filename)
    f.save(os.path.join(app.config['BACKLOG_PATH'], name))

    add_job_to_queue(TYPE, shortname, username, name)
    return render_template('biorxiv2carrel-queue.html', username=username, shortname=shortname)

# list_to_pairs takes a list like ['aaa', 123, 'bbb', 234, 'ccc', 345, ...]
# interprets it as a list of key-value pairs, and returns
# the list of those pairs e.g. [('aaa', 123), ('bbb', 234), ('ccc', 345), ...]
def list_to_pairs(a):
    i = iter(a)
    return list(zip(i, i))

# keep_non_zero takes a list of pairs [(a,b), (c,d), ...] and returns a list
# of pairs where the second element is > 0
def keep_positive(a):
    return [(x,y) for x,y in a if y > 0]

@app.route('/gutenberg')
def gutenberg():
    # configure
    FACETFIELD = ['facet_subject', 'facet_author', 'facet_classification']
    ROWS = 499

    # initialize
    query = request.args.get('query', '')
    solr = pysolr.Solr(url=app.config['SOLR_URL_GUTENBERG'])

    if query == '':
        return render_template('gutenberg.html', query='', results=[])

    # build the search options
    search_options = {
            'facet.field': FACETFIELD,
            'facet': 'true',
            'rows': ROWS
    }

    response = solr.search(query, **search_options)

    facets = {facet: keep_positive(list_to_pairs(v)) for facet,v in response.facets['facet_fields'].items()}

    total_hits = response.hits
    num_displayed = len(response)

    # sort the subject and classification field for these results
    for doc in response.docs:
        doc.get('classification', []).sort()
        doc.get('subject', []).sort()

    return render_template('gutenberg-results.html',
            query=query,
            total_hits=total_hits,
            num_displayed=num_displayed,
            results=response.docs,
            facets=facets)

@app.route('/create/gutenberg', methods=['GET', 'POST'])
@login_required
def create_gutenberg():
    TYPE = 'gutenberg'

    # initialize
    # query is passed as a param for GET requests and as
    # as a form vaule for POSTs.
    shortname = request.form.get('shortname', '')
    username = current_user.username

    if request.method != 'POST' or shortname == '':
        query = request.args.get('query', '')
        return render_template('gutenberg-create.html', query=query)

    query = request.form.get('query', '')
    shortname = secure_filename(shortname)
    add_job_to_queue(TYPE, shortname, username, query)
    return render_template('gutenberg-queue.html', username=username, shortname=shortname)


@app.route('/cord')
def cord_search():
    FACETFIELD = ['facet_journal', 'year', 'facet_authors', 'facet_keywords', 'facet_entity', 'facet_type', 'facet_sources']
    FIELDS = 'id,title,doi,urls,date,journal,abstract,sources,pmc_json,pdf_json,sha'
    ROWS = 49

    # initialize
    query = request.args.get('query', '')
    solr = pysolr.Solr(url=app.config['SOLR_URL_CORD'])

    # display the home page
    if query == '':
        return render_template('cord.html', query='', results=[])

    # build the search options
    search_options = {
            'facet.field': FACETFIELD,
            'fl': FIELDS,
            'facet': 'true',
            'rows': ROWS
    }

    response = solr.search(query, **search_options)

    facets = {facet: keep_positive(list_to_pairs(v)) for facet,v in response.facets['facet_fields'].items()}
    total_hits = response.hits
    num_displayed = len(response)

    return render_template('cord-results.html',
            query=query,
            total_hits=total_hits,
            num_displayed=num_displayed,
            results=response.docs,
            facets=facets)

@app.route('/create/cord', methods=['GET', 'POST'])
@login_required
def create_cord():
    TYPE = 'cord'

    # initialize
    # query is passed as a param for GET requests and as
    # as a form vaule for POSTs.
    shortname = request.form.get('shortname', '')
    username = current_user.username

    if request.method != 'POST' or shortname == '':
        query = request.args.get('query', '')
        return render_template('cord-create.html', query=query)

    query = request.form.get('query', '')
    shortname = secure_filename(shortname)
    add_job_to_queue(TYPE, shortname, username, query)
    return render_template('cord-queue.html', username=username, shortname=shortname)


