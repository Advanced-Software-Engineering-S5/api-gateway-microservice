from flask import Blueprint, redirect, render_template, current_app
from flask_jwt_extended import jwt_optional
from api_gateway.auth import current_user
# from api_gateway.classes.notification_retrieval import fetch_notifications

home = Blueprint('home', __name__)


@home.route('/')
@jwt_optional
def index():
    if current_user is not None and hasattr(current_user, 'id'):
        if hasattr(current_user, 'is_admin') and current_user.is_admin == True:
            return redirect("/authority")
        # restaurants = db.session.query(Restaurant)
        # notifs = fetch_notifications(current_app, current_user, unread_only=True)
    else:
        restaurants = []
        notifs = []
    return render_template("index.html", restaurants=restaurants, notifications=notifs)
    return render_template("index.html")


@home.route('/signup')
def signup():
    return render_template("signup.html")