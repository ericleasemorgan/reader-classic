from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth

from app import app
from models import User

oauth = OAuth(app)
# the client_id and client_secret are provided via the config file.
if app.debug:
    # rely on the config file to supply the exact port we are running on
    oauth.register(name="orcid")
else:
    oauth.register(
        name="orcid",
        authorize_url="https://orcid.org/oauth/authorize",
        access_token_url="https://orcid.org/oauth/token",
    )

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# load_user turns a user id in the session into a user object in memory.
# returning None means the user doesn't exist.
@login_manager.user_loader
def load_user(user_id):
    if user_id is not None and user_id != "":
        return User.FromID(user_id)
    return None
