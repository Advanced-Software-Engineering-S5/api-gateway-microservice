from flask import Blueprint, redirect, render_template, request
#from monolith.database import db, User
from api_gateway.classes.user import User
from api_gateway.auth import admin_required
from api_gateway.forms import SearchUserForm
from api_gateway.classes.authority_frontend import mark_user, search_user, INCUBATION_PERIOD_COVID
from collections import namedtuple
import requests, os

authority = Blueprint('authority', __name__)


@authority.route('/authority')
@admin_required
def _authority(message=''):
    return render_template("authority.html")


FilterUser = namedtuple("FilterUser", ["email", "phone", "fiscal_code"])


@authority.route('/authority/search_user', methods=['GET', 'POST'])
@admin_required
def _search_user(message=''):
    form = SearchUserForm()
    if request.method == 'POST':

        if form.validate_on_submit():
            filter_user = FilterUser(email=form.data['email'],
                                     phone=form.data['fiscal_code'],
                                     fiscal_code=form.data['fiscal_code'])
            # form.populate_obj(filter_user)
            user, error_message = search_user(filter_user)
            if user == None:
                return render_template("error.html", error_message=error_message)
            else:
                return render_template("single_user_for_authority.html", user=user)

    return render_template('create_user.html', form=form)


@authority.route('/authority/mark/<marked_user_id>')
@admin_required
def _mark(marked_user_id):
    message, user = mark_user(marked_user_id)

    if message != '':
        return render_template("error.html", error_message=message)
    else:
        return render_template("single_user_for_authority.html", user=user)


@authority.route('/authority/trace_contacts/<user_id>')
@admin_required
def _get_contact_list(userculo_id):
    users_at_risk = requests.get(f"http://{os.environ.get('GOS_RESERVATION')}/contact_tracing/{userculo_id}") 
    return render_template("users_for_authority.html", users=users_at_risk)
