from flask import (Flask,render_template, request)
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_httpauth import HTTPBasicAuth
from passlib.apache import HtpasswdFile
import os.path
import pysolr

app = Flask(__name__)
app.config.from_envvar('READER_CONFIG')
app.url_map.strict_slashes = False

auth = HTTPBasicAuth(realm="Authentication Required")

htpasswd = None
htpasswd_filename = app.config.get('HTPASSWD_FILE', None)
if htpasswd_filename:
    htpasswd = HtpasswdFile(htpasswd_filename)

@auth.verify_password
def verify_password(username, password):
    if htpasswd:
        return htpasswd.check_password(username, password)
    # only allow no password file if in debugging mode.
    # this is to "fail-safe" in production
    # if we are not in debug mode, every auth request fails
    return app.debug

##### Template helpers

NUMERALS = {1:'I', 2:'II', 3:'III', 4:'IV', 5:'V',
        6:'VI', 7:'VII', 8:'VIII', 9:'IX', 10:'X',
        11:'XI', 12:'XII', 13:'XIII', 14:'XIV', 15:'XV',
        16:'XVI', 17:'XVII', 18:'XVIII', 19:'XIX', 20:'XX'}

@app.template_filter('roman_numeral')
def roman_numeral(n):
    return NUMERALS.get(n, '')


##### Route Handlers

@app.route('/')
def index():
    return render_template('home.html')

def add_job_to_queue(job_type, shortname, username, extra):
    now = datetime.now().strftime("%Y-%m-%d\t%H:%M")
    # since shortname is user supplied, different users many use the same name
    shortname = secure_filename(shortname)
    with open(os.path.join(app.config['TODO_PATH'], shortname + ".tsv"), mode="w") as f:
        f.write("\t".join([job_type, shortname, now, username, extra]))
        f.write("\n")

@app.route('/create/url2carrel', methods=['GET', 'POST'])
@auth.login_required
def url2carrel():
    TYPE = 'url2carrel'
    shortname = request.form.get('shortname', '')
    target_url = request.form.get('url', '')
    username = auth.username()

    if request.method != 'POST' or shortname == '' or target_url == '':
        return render_template('url2carrel.html')
    shortname = secure_filename(shortname)
    add_job_to_queue(TYPE, shortname, username, target_url)
    return render_template('urls2carrel-queue.html', username=username, shortname=shortname)

@app.route('/create/urls2carrel', methods=['GET', 'POST'])
@auth.login_required
def urls2carrel():
    TYPE = 'urls2carrel'

    # initialize
    shortname  = request.form.get('shortname', '')
    queue = request.form.get('queue', '')
    username = auth.username()

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
@auth.login_required
def zip2carrel():
    TYPE = 'zip2carrel'

    # initialize
    shortname = request.form.get('shortname', '')
    queue = request.form.get('queue', '')
    username = auth.username()

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
@auth.login_required
def file2carrel():
    TYPE = 'file2carrel'

    shortname = request.form.get('shortname', '')
    queue = request.form.get('queue', '')
    username = auth.username()

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
@auth.login_required
def trust2carrel():
    TYPE = 'trust'

    # initialize
    shortname = request.form.get('shortname', '')
    queue = request.form.get('queue', '')
    username = auth.username()

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
@auth.login_required
def biorxiv2carrel():
    TYPE = 'biorxiv'

    shortname = request.form.get('shortname', '')
    queue = request.form.get('queue', '')
    username = auth.username()

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
@auth.login_required
def create_gutenberg():
    TYPE = 'gutenberg'

    # initialize
    # query is passed as a param for GET requests and as
    # as a form vaule for POSTs.
    shortname = request.form.get('shortname', '')
    username = auth.username()

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
@auth.login_required
def create_cord():
    TYPE = 'cord'

    # initialize
    # query is passed as a param for GET requests and as
    # as a form vaule for POSTs.
    shortname = request.form.get('shortname', '')
    username = auth.username()

    if request.method != 'POST' or shortname == '':
        query = request.args.get('query', '')
        return render_template('cord-create.html', query=query)

    query = request.form.get('query', '')
    shortname = secure_filename(shortname)
    add_job_to_queue(TYPE, shortname, username, query)
    return render_template('cord-queue.html', username=username, shortname=shortname)

