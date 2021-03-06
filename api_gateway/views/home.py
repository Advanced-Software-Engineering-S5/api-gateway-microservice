from os import remove
from api_gateway.classes.restaurant import Restaurant
from flask import Blueprint, redirect, render_template, current_app
from flask_jwt_extended import jwt_optional
from api_gateway.auth import current_user
from api_gateway.classes.notifications import fetch_notifications

home = Blueprint('home', __name__)


@home.route('/')
def index():
    restaurants = []
    notifs = []
    if current_user is not None and hasattr(current_user, 'id'):
        if hasattr(current_user, 'is_admin') and current_user.is_admin == True:
            return redirect("/authority")
        restaurants = Restaurant.getAll()
        notifs = fetch_notifications(current_user, unread_only=True)
    return render_template("index.html", restaurants=restaurants, notifications=notifs)


@home.route('/signup')
def signup():
    return render_template("signup.html")