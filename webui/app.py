from flask import Flask, session, render_template, request, g
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
# get external host name so we can make correct redirect urls for oauth
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)
app.config.from_envvar("READER_CONFIG")
app.url_map.strict_slashes = False

app.config["USE_SESSION_FOR_NEXT"] = 1

##### Template helpers

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
