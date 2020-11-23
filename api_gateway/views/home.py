from os import remove
from api_gateway.classes.restaurant import Restaurant
from flask import Blueprint, redirect, render_template, current_app
from flask_jwt_extended import jwt_optional
from api_gateway.auth import current_user

home = Blueprint('home', __name__)


@home.route('/')
def index():
    if current_user and hasattr(current_user, 'id'):
        if hasattr(current_user, 'is_admin') and current_user.is_admin == True:
            return redirect("/authority")
        restaurants = Restaurant.getAll()
        restaurants = ["aaa"]
        # notifs = fetch_notifications(current_app, current_user, unread_only=True)
        notifs = []
    else:
        restaurants = []
        notifs = []
        return render_template("error.html")
    return render_template("index.html", restaurants=restaurants, notifications=notifs)


@home.route('/signup')
def signup():
    return render_template("signup.html")