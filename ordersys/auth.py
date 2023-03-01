import os
import json
import requests

from functools import wraps
from flask import *
from dotenv import load_dotenv
from ordersys.db import get_db
from ordersys.user import User
from flask_login import *
from oauthlib.oauth2 import WebApplicationClient

load_dotenv()
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")
URL = os.environ.get("BASE_URL")

client = WebApplicationClient(GOOGLE_CLIENT_ID)

bp = Blueprint('auth', __name__, url_prefix='/auth')

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin():
            return current_app.login_manager.unauthorized()

        if callable(getattr(current_app, "ensure_sync", None)):
            return current_app.ensure_sync(func)(*args, **kwargs)
        return func(*args, **kwargs)

    return decorated_view

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        if request.form['login-type'] == 'dev':
            email = request.form['email']
            user = User.get(email, param_type=1)

            if not user:
                flash('You are not a designated Project Manager. Please contact Matt Lamparter.', 'error')
                return redirect(url_for("auth.login"))

            login_user(user)

            if user.is_admin(): # super user / admin
                return redirect(url_for('admin.index'))
            else:
                return redirect(url_for('project.index'))
        
        else:
            google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
            authorization_endpoint = google_provider_cfg["authorization_endpoint"]
            request_uri = client.prepare_request_uri(
                authorization_endpoint,
                redirect_uri = URL + url_for("auth.callback"),
                scope = ["openid", "email", "profile"],
            )
        
            return redirect(request_uri)
    
    return render_template('auth/login.html')

@bp.route('/login/callback')
def callback():
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response = URL + request.url.split(request.host)[1],
        redirect_url = URL + url_for("auth.callback"),
        code = request.args.get("code")
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        email = userinfo_response.json()["email"]
    else:
        flash('Unable to verify email.')
    
    user = User.get(email, param_type=1)

    if not user:
        flash('You are not a designated Project Manager. Please contact <a>Matt Lamparter</a>.')
        return redirect(url_for("auth.login"))

    login_user(user)

    if user.auth_level == 0: # super user / admin
        return redirect(url_for('admin.index'))
    else:
        return redirect(url_for('project.index'))

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

    


