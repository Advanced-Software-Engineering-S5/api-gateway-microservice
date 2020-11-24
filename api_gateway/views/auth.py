import os, requests
from flask.helpers import url_for
from flask import Blueprint, session, request, make_response, render_template
from werkzeug.utils import redirect
from ..classes.user import User
from api_gateway.views import home
from datetime import datetime
from flask_jwt_extended import set_access_cookies, decode_token
from api_gateway.auth import currently_logged_in, login_required, current_user
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

    #Reset the cookies if we want to login again
    response = make_response(render_template('login.html', form=form))
    response.set_cookie('gooutsafe_jwt_token', "", expires=0)
    response.set_cookie("csrf_access_token", "", expires=0)
    response.status_code = 200
    return response

@auth.route('/unregister/<id>')
@login_required
def delete(id):
    if current_user.id != int(id):
        return render_template("error.html", error_message="You are not supposed to be here")
    if current_user.is_positive:
        return render_template("error.html", error_message="You cannot unregister if marked positive")
    # logout_user()
    # delete_user(int(id))
    return redirect('/')

@auth.route('/logout')
def logout():
    # TODO: Add cookie removal and remove from currently_logged_in.
    response = make_response()
    response.set_cookie('gooutsafe_jwt_token', "", expires=0)
    response.set_cookie("csrf_access_token", "", expires=0)
    response.status_code = 301
    response.location = url_for("home.index")
    currently_logged_in[str(current_user.id)] = None
    return response