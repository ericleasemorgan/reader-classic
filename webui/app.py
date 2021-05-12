from flask import Flask, session, render_template, request, g
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
# get external host name so we can make correct redirect urls for oauth
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)
app.config.from_envvar("READER_CONFIG")
app.url_map.strict_slashes = False

app.config["USE_SESSION_FOR_NEXT"] = 1

##### Template helpers

@app.template_filter("formatwithcommas")
def formatwithcommas(n):
    try:
        return "{:,}".format(int(n))
    except:
        return n

    for fragment, desc in DESCRIPTIONS.items():
        if filepath.endswith(fragment):
            return desc
    return ""
NUMERALS = {
    1: "I",
    2: "II",
    3: "III",
    4: "IV",
    5: "V",
    6: "VI",
    7: "VII",
    8: "VIII",
    9: "IX",
    10: "X",
    11: "XI",
    12: "XII",
    13: "XIII",
    14: "XIV",
    15: "XV",
    16: "XVI",
    17: "XVII",
    18: "XVIII",
    19: "XIX",
    20: "XX",
}


@app.template_filter("roman_numeral")
def roman_numeral(n):
    return NUMERALS.get(n, "")


DESCRIPTIONS = {
    # study carrel root
    "index.html": "Narrative report; <span style='color: darkred;text-decoration: underline'><strong>read this second</strong></span>",
    "cache": 'Original versions of analyzed files; file name roots are used as "keys" throughout the carrel',
    "pos": "Part-of-speech file(s); importable into your spreadsheet, database, or analysis application",
    "standard-output.txt": "Simple narrative report; <span style='color: darkred;text-decoration: underline'><strong>start here</strong></span>",
    "standard-error.txt": "Log file; if this carrel is dysfunctional, then send this file to Eric Morgan &lt;emorgan@nd.edu&gt;",
    "study-carrel.zip": "Study carrel as a single file; download this file for offline reading and more thorough use &amp; understanding",
    "provenance.tsv": "A record of who created this carrel, when, and how",
    "MANIFEST.htm": "Description of all the files in a study carrel; a verbose version of this page; <span style='color: darkred;text-decoration: underline'><strong>read this third</strong></span>",
    "adr": "Email address file(s); importable into your spreadsheet, database, or analysis application",
    "etc": "Database file, stop words file, etc; power-users will love these files",
    "figures": "Charts &amp; graphs used in the narrative report",
    "LICENSE": "GNU Public License",
    # figures
    "sizes-histogram.png": "Histogram of <strong>document sizes</strong>",
    "sizes-boxplot.png": "Box plot of <strong>document sizes</strong>",
    "topics.png": 'Pie chart of topic modeling <strong>"themes"</strong>',
    "unigrams.png": "Word cloud of most <strong>words</strong>",
    "proper-nouns.png": "Word cloud of most frequent <strong>proper nouns</strong>",
    "pronouns.png": "Word cloud of most frequent <strong>pronouns</strong>",
    "nouns.png": "Word cloud of most frequent <strong>nouns</strong>",
    "keywords.png": "Word cloud of most frequent <strong>keywords</strong>",
    "adjectives.png": "Word cloud of most frequent <strong>adjectives</strong>",
    "adverbs.png": "Word cloud of most frequent <strong>adverbs</strong>",
    "bigrams.png": "Word cloud of most frequent <strong>two-word phrases</strong>",
    "flesch-boxplot.png": "Box plot of <strong>readability scores</strong>",
    "flesch-histogram.png": "Histogram of <strong>readability scores</strong>",
    "verbs.png": "Word cloud of most frequent <strong>verbs</strong>",
    # sub reports
    "adverbs.htm": "HTML table of most frequent <strong>adverbs</strong>",
    "verbs.htm": "HTML table of most frequent <strong>verbs</strong>",
    "adjective-noun.htm": "HTML table of most frequent <strong>adjective-noun combinations</strong>",
    "noun-verb.htm": "HTML table of most frequent <strong>noun-verb combinations</strong>",
    "adjectives.htm": "HTML table of most frequent <strong>adjectives</strong>",
    "proper-nouns.htm": "HTML table of most frequent <strong>proper nouns<strong>",
    "pronouns.htm": "HTML table of most frequent <strong>pronouns</strong>",
    "nouns.htm": "HTML table of most frequent <strong>nouns</strong>",
    "keywords.htm": "HTML table of most frequent <strong>keywords</strong>",
    "bigrams.htm": "HTML table of most frequent <strong>two-word phrases</strong>",
    "quadgrams.htm": "HTML table of most frequent <strong>four-word phrases</strong>",
    "questions.htm": "HTML table of <strong>questions</strong>",
    "search.htm": "Rudimentary <strong>search interface</strong>",
    "topic-model.htm": "Rudimentary <strong>topic modeling interface</strong>",
    "unigrams.htm": "HTML table of most frequent <strong>words</strong>",
    "trigrams.htm": "HTML table of most frequent <strong>three-word phrases</strong>",
    "entities.htm": "HTML table of most frequent <strong>named-entities and their types</strong>",
    "bibliographics.htm": 'HTML table of bibliographics; a rudimentary <strong>"library catalog"<strong>',
    "adverbs.tsv": "TSV file of most frequent <strong>adverbs</strong> and their counts",
    "verbs.tsv": "TSV file of most frequent <strong>verbs</strong> and their counts",
    "adjective-noun.tsv": "TSV file of most frequent <strong>adjective-noun combinations</strong> and their counts",
    "noun-verb.tsv": "TSV file of most frequent <strong>noun-verb combinations</strong> and their counts",
    "adjectives.tsv": "TSV file of most frequent <strong>adjectives</strong> and their counts",
    "proper-nouns.tsv": "TSV file of most frequent <strong>proper nouns</strong> and their counts",
    "pronouns.tsv": "TSV file of most frequent <strong>pronouns</strong> and their counts",
    "nouns.tsv": "TSV file of most frequent <strong>nouns</strong> and their counts",
    "keywords.tsv": "TSV filee of most frequent <strong>keywords</strong> and their counts",
    "bigrams.tsv": "TSV filee of most frequent <strong>two-word phrases</strong> and their counts",
    "quadgrams.tsv": "TSV file of most frequent <strong>four-word phrases</strong> and their counts",
    "questions.tsv": "TSV file of <strong>questions</strong>",
    "unigrams.tsv": "TSV file of most frequent <strong>words</strong> and their counts",
    "trigrams.tsv": "TSV file of most frequent <strong>three-word phrases</strong> and their counts",
    "entities.tsv": "TSV file of most frequent <strong>named-entities and their types</strong> and their counts",
    "bibliographics.tsv": 'TSV file of bibliographics; a rudimentary <strong>"library catalog"</strong>',
    # etc
    "model-data.txt": "Data file used by topic modeling interface",
    "queries.sql": "SQL statements used to create the simple narrative report; great for learning how to query reader.db",
    "reader.db": "Cross-platform SQLite database file; the answers to your research questions are probably in here",
    "reader.sql": "SQL statements denoting the structure of reader.db; great for learning about reader.db",
    "reader.txt": "A concatenation of all plain text files used for analysis; the entire corpus in a single file ",
    "report.txt": "A copy of the simple narrative report",
    "stopwords.txt": 'A list of "function" words excluded from analysis',
    "reader.zip": "Study carrel as a single file; download this file for offline reading and more thorough use &amp; understanding",
    # defaults,
    "txt": 'Plain text version(s) of cached file(s); file(s) used for "distant reading" purposes',
    "tsv": "Tab-delimited (TSV) files used in narrative report",
    "ent": "Name-entity file(s); TSV file(s) importable into your spreadsheet, database, or analysis application",
    "bib": "Bibliographic file(s); TSV file(s) importable into your spreadsheet, database, or analysis application",
    "pdf": "Portable Document File; a file usually designed for printing",
    "html": "HTML file readable with your Web browser",
    "htm": "Sub-reports of the narrative report",
    "docx": "A Microsoft Word document",
    "css": "Cascading stylesheet file(s) for use by the narrative report",
    "js": "Javascript file(s) used by the narrative report",
    "urls": "URL file(s); importable into your spreadsheet, database, or analysis application",
    "wrd": "Keyword file(s); TSV file(s) importable into your spreadsheet, database, or analysis application",
}


@app.template_filter("file_description")
def file_description(filepath):
    for fragment, desc in DESCRIPTIONS.items():
        if filepath.endswith(fragment):
            return desc
    return ""
