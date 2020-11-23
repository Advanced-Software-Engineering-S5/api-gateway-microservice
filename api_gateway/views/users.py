from api_gateway.views.auth import login
from datetime import datetime
from api_gateway.classes.restaurant import Restaurant
from api_gateway.classes.exceptions import GoOutSafeError, FormValidationError
from api_gateway.classes.user import User
from flask import Blueprint, redirect, render_template, request, current_app
from api_gateway.auth import current_user, login_required
from api_gateway.forms import OperatorForm, UserForm, UserProfileEditForm
# from api_gateway.classes.notification_retrieval import *


users = Blueprint('users', __name__)

@users.route('/users')
def _users():
    users = User.all()
    return render_template("users.html", users=users)
 

@users.route('/create_user', methods=['GET', 'POST'])
def create_user():
    form = UserForm()
    if request.method == 'POST':
        try:
            dateofbirth = datetime(form.dateofbirth.data.year, form.dateofbirth.data.month, form.dateofbirth.data.day)
            id = User.create(email=form.email.data, \
                firstname=form.firstname.data, lastname=form.lastname.data, \
                password=form.password.data, fiscal_code=form.fiscal_code.data, \
                phone=str(form.phone.data), dateofbirth=dateofbirth)
            login()
            return redirect('/')
        except FormValidationError:
            return render_template('create_user.html', form=form)
        except Exception as e:
            return render_template("error.html", error_message=str(e))
            
    return render_template('create_user.html', form=form)


@users.route('/create_operator', methods=['GET', 'POST'])
def create_operator():
    form = OperatorForm()
    if request.method == 'POST':
        try:
            dateofbirth = datetime(form.dateofbirth.data.year, form.dateofbirth.data.month, form.dateofbirth.data.day)
            u = Restaurant.create(form.email.data, \
                form.firstname.data, form.lastname.data, \
                form.password.data, dateofbirth, \
                form.name.data, form.lat.data, form.lon.data, \
                form.phone.data, extra_info=form.extra_info.data)
            login()
            return redirect('/')
        except GoOutSafeError as e:
            return render_template('create_operator.html', form=form)
        except Exception as e:
            return render_template("error.html", error_message=str(e))

    return render_template('create_operator.html', form=form)


@users.route('/users/edit/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.id != int(user_id):
        return render_template("error.html", error_message="You aren't supposed to be here!")

    form = UserProfileEditForm(obj=current_user)
    if request.method == 'POST':
        try:
            # edit_user_data(form, user_id)
            return redirect('/users/edit/' + user_id)
        except GoOutSafeError:
            return render_template("useredit.html", form=form)
        except Exception as e:
            return render_template("error.html", error_message=str(e))
    return render_template("useredit.html", form=form)

"""
@users.route('/notifications', methods=['GET'])
@login_required
def all_notifications():
    try:
        if hasattr(current_user, 'is_admin') and current_user.is_admin == True:
            # redirect authority to another page
            return redirect("/authority")
        notifs = fetch_notifications(current_app, current_user, unread_only=False)
        return render_template('notifications_list.html', notifications_list=notifs, message='You were in contact with a positive user in the following occasions:')
    except GoOutSafeError as e:
        return render_template("error.html", error_message=str(e))

@users.route('/notifications/<notification_id>', methods=['GET'])
@login_required
def get_notification(notification_id):
    # show notification detail view and mark notification as seen
    try:
        notif = getAndSetNotification(notification_id)
        return render_template('notification_detail.html', notification=notif)
    except GoOutSafeError as e:
        return render_template("error.html", error_message=str(e))
        """
