import os, requests
from flask import Blueprint, session, request, make_response, render_template
from ..classes.user import User
from api_gateway.views import home
from datetime import datetime
from flask_jwt_extended import set_access_cookies, decode_token
from api_gateway.auth import currently_logged_in
from api_gateway.forms import LoginForm

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # TODO: Must work with login form
    form = LoginForm()
    # Ugliest and unsafe hack
    validate = True if not form.data['csrf_token'] else form.validate
    if request.method == 'POST' and validate:
        email, password = form.data['email'], form.data['password']
        jwt_token = requests.post(f"{User.BASE_URL}/user/auth", json=dict(email=email, password=password))
        if jwt_token.status_code == 200:
            resp = make_response()
            user_id = decode_token(jwt_token.json())['identity']
            user = User.get(id=user_id)
            user.is_authenticated = True
            currently_logged_in[str(user_id)] = user
            set_access_cookies(resp, jwt_token.json())
            resp.status_code = 301
            resp.location = '/'
            return resp
        else:
            form.email.errors = ("The email or password inserted is invalid",)
            return render_template('login.html', form=form), 401

    return render_template('login.html', form=form), 200


def logout():
    # TODO: Add cookie removal and remove from currently_logged_in.
    pass