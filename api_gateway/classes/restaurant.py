from __future__ import annotations
from os import stat
from api_gateway.classes.user import User

from sqlalchemy.sql.functions import user
from api_gateway.classes.exceptions import GoOutSafeError
import requests, json, os
from dataclasses import dataclass, field, fields
from datetime import datetime, time
from typing import Optional



def convert_json(j):
    t = j['avg_stay_time']
    j['avg_stay_time'] = time(*[int(g) for g in t.split(':')])


@dataclass(eq=False, order=False)
class Restaurant:
    """
    Restaurant abstraction over REST endpoints.
    Do not return such instances and do not pass them around as function arguments. Each procedure should do its own
    Restaurant.get call.
    """

    #BASE_URL = f"{os.environ.get('GOS_RESTAURANT')}"
    BASE_URL = "http://restaurant:5000"

    id : int
    name : str
    lat : float
    lon : float
    phone : str
    extra_info : Optional[str]
    avg_stay_time : time
    avg_stars : float
    num_reviews : int

    #This always represents what's in the database (hopefully)
    invariant: dict = field(init=False, repr=False)

    @staticmethod
    def getAll():
        """
        Gets an User instance if it is found, otherwise returns None.
        Arguments are all keyword arguments.

        Example:
            usr = User.get(id=1)
            usr = User.get(email='op@op.com')
        """
        req = requests.get(f"{Restaurant.BASE_URL}/restaurants")
        l = []
        if req.status_code == 200:
            json_dict = req.json()
            for j in json_dict:
                convert_json(j)
                r = Restaurant(**j)
                r.invariant = j
                l.append(r)
        return l

    @staticmethod
    def get(id) -> Restaurant:
        """
        Gets an User instance if it is found, otherwise returns None.
        Arguments are all keyword arguments.

        Example:
            usr = User.get(id=1)
            usr = User.get(email='op@op.com')
        """
        req = requests.get(f"{Restaurant.BASE_URL}/restaurants/{id}")
        if req.status_code == 200:
            json_dict = req.json()
            convert_json(json_dict)
            r = Restaurant(**json_dict)
            r.invariant = json_dict
            return r
        return None


    @staticmethod
    def update(id, tables, phone=None, extra_info=None):
        """
        Updates the user database with the modified fields.
        If the update fails the instance is reverted to a state consistent with the db (hopefully).

        Example:
            usr.firstname = "aldo"
            usr.submit()
        """

        body = {"tables":[]}
        i = 1
        for t in tables:
            body['tables'].append({"table_id":i, "seats":t.seats})
            i = i + 1

        if phone:
            body['phone'] = phone
        if extra_info:
            body['extra_info'] = extra_info

        req = requests.put(f"{Restaurant.BASE_URL}/restaurants/{id}", json=body)
        if req.status_code != 201:
            raise GoOutSafeError()

    def update_review(self, stars_no):
        # updates restaurant view with newly written review so that user can see its change immediately
        self.num_reviews += 1
        self.avg_stars = 1/self.num_reviews * \
            (self.avg_stars * (self.num_reviews-1) + stars_no)
        return self
    
    @staticmethod
    def create(email, firstname, lastname, password, dateofbirth, name, lat, lon, phone, extra_info=None):
        body_restaurant = {
            'name': name,
            'lat': lat,
            'lon': lon,
            'phone': phone,
            'extra_info': extra_info
        }

        req = requests.post(f"{Restaurant.BASE_URL}/new", data=body_restaurant)
        if req.status_code != 201:
            return None
        
        restaurant_id = req.json()
        ret = User.create(email, firstname=firstname, \
                lastname=lastname, password=password, dateofbirth=dateofbirth, \
                restaurant_id=restaurant_id)
        if not ret:
            # user creation didn't go well, reverting restaurant db
            Restaurant.delete(restaurant_id)
        return User.get(id=ret)


    @staticmethod
    def delete(restaurant_id):
        req = requests.delete(f"{Restaurant.BASE_URL}/restaurants/{restaurant_id}")
        if req.status_code != 200:
            raise GoOutSafeError()
        


@dataclass(eq=False, order=False)
class RestaurantTable:
    """
    Restaurant abstraction over REST endpoints.
    Do not return such instances and do not pass them around as function arguments. Each procedure should do its own
    Restaurant.get call.
    """

    BASE_URL = f"http://{os.environ.get('GOS_RESTAURANT')}"

    table_id : int
    restaurant_id : int
    seats : int

    #This always represents what's in the database (hopefully)
    invariant: dict = field(init=False, repr=False)

    @staticmethod
    def get(restaurant_id):
        req = requests.get(f"{RestaurantTable.BASE_URL}/restaurants/tables/{restaurant_id}")

        l = []
        if req.status_code == 200:
            json_dict = req.json()
            for j in json_dict:
                r = RestaurantTable(**j)
                r.invariant = j
                l.append(r)
        return l


@dataclass(eq=False, order=False)
class Review:

    BASE_URL = f"http://{os.environ.get('GOS_RESTAURANT')}"

    reviewer_id : int
    restaurant_id : int
    stars : int
    text_review : str
    marked : bool

    invariant: dict = field(init=False, repr=False)

    @staticmethod
    def add(restaurant_id, user_id, stars, text=None):
        body = {"reviewer_id":user_id, "stars":stars}
        if text:
            body['text_review'] = text
        req = requests.post(f"{Review.BASE_URL}/reviews/{restaurant_id}", data=body)
        if req.status_code != 201:
            raise GoOutSafeError

    @staticmethod
    def get(restaurant_id, user_id):
        req = requests.get(f"{Review.BASE_URL}/reviews/{restaurant_id}?user_id={user_id}")

        if req.status_code == 200:
            json_dict = req.json()
            convert_json(json_dict)
            r = Review(**json_dict)
            r.invariant = json_dict
            return r
        return None

    @staticmethod
    def get(restaurant_id):
        req = requests.get(f"{Review.BASE_URL}/reviews/{restaurant_id}")

        l = []
        if req.status_code == 200:
            json_dict = req.json()
            for j in json_dict:
                r = Review(**j)
                r.invariant = j
                l.append(r)
        return l

