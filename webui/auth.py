from flask_login import LoginManager
from passlib.apache import HtpasswdFile

from app import app
from models import User


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# load_user turns a user id in the session into a user object in memory.
# None means the user doesn't exist.
@login_manager.user_loader
def load_user(user_id):
    if user_id is not None and user_id != "":
        return User.FromID(user_id)
    return None


# set up auth to use existing apache user file
htpasswd = None
htpasswd_filename = app.config.get('HTPASSWD_FILE', None)
if htpasswd_filename:
    htpasswd = HtpasswdFile(htpasswd_filename)

def verify_password(username, password):
    if htpasswd:
        return htpasswd.check_password(username, password)
    # only allow no password file if in debugging mode.
    # this is to "fail-safe" in production
    # if we are not in debug mode, every auth request fails
    return app.debug

