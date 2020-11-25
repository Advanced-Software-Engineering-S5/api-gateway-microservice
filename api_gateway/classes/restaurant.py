from __future__ import annotations
from api_gateway.classes.user import User
from api_gateway.classes.exceptions import GoOutSafeError
import os
from dataclasses import dataclass, field
from datetime import time
from typing import Optional
from api_gateway.classes.utils import *


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

    BASE_URL = f"http://{os.environ.get('GOS_RESTAURANT')}"


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
        Gets all the Restaurant instance found, otherwise returns None.
        """
        req = safe_get(f"{Restaurant.BASE_URL}/restaurants")
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
    def get(id : int) -> Restaurant:
        """
        Gets a Restauant instance bby id if it is found, otherwise returns None.

        Example:
            r = Restaurant.get(1)
        """
        req = safe_get(f"{Restaurant.BASE_URL}/restaurants/{id}")
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
        Updates the restaurant database with the modified fields.
        If the update fails the instance is reverted to a state consistent with the db (hopefully).
        """

        body = {"tables":[]}
        i = 1
        while tables.get('table_' + str(i)) != None:
            body['tables'].append({"table_id":i, "seats": int(tables.get('table_' + str(i)))})
            i = i + 1

        if phone:
            body['phone'] = str(phone)
        if extra_info:
            body['extra_info'] = str(extra_info)

        req = safe_put(f"{Restaurant.BASE_URL}/restaurants/{id}", json=body)
        if req.status_code != 201:
            raise GoOutSafeError()

    def update_review(self, stars_no):
        # updates restaurant view with newly written review so that user can see its change immediately
        self.num_reviews += 1
        self.avg_stars = 1/self.num_reviews * \
            (self.avg_stars * (self.num_reviews-1) + stars_no)
        return self

    @staticmethod
    def delete(restaurant_id):
        """Deletes a Restaurant with id restaurant_id

        Args:
            restaurant_id (int): the restaurant id

        Raises:
            GoOutSafeError: if the deletion cannot be performed
        """

        req = safe_delete(f"{Restaurant.BASE_URL}/restaurants/{restaurant_id}")
        if req.status_code != 200:
            raise GoOutSafeError(str(req))
    
    @staticmethod
    def create(email, firstname, lastname, password, dateofbirth, name, lat, lon, phone, extra_info=None):
        """Creates a new restaurant by the given parameters and returns the User object.
        If the User creation cannot be performed the db is reverted to a consistent state.

        Raises:
            Exception: if the creation cannot be performed

        Returns:
            User: the restaurant operator
        """
        body_restaurant = {
            'name': str(name),
            'lat': float(lat),
            'lon': float(lon),
            'phone': str(phone),
            'extra_info': str(extra_info)
        }

        req = safe_post(f"{Restaurant.BASE_URL}/restaurants/new", json=body_restaurant)
        if req.status_code != 201:
            raise Exception(str(req))
        
        restaurant_id = req.json()
        ret = User.create(email=email, firstname=firstname, \
                lastname=lastname, password=password, dateofbirth=dateofbirth, \
                restaurant_id=restaurant_id)
        logging.warning(f"{ret}")
        if not ret:
            # user creation didn't go well, reverting restaurant db
            Restaurant.delete(restaurant_id)
            return None
        
        return User.get(id=ret)


@dataclass(eq=False, order=False)
class RestaurantTable:
    """
    RestaurantTable abstraction over REST endpoints.
    Do not return such instances and do not pass them around as function arguments.
    """

    table_id : int
    restaurant_id : int
    seats : int

    #This always represents what's in the database (hopefully)
    invariant: dict = field(init=False, repr=False)

    @staticmethod
    def get(restaurant_id):
        """Returns the table list for the restaurant `restaurant_id`

        Args:
            restaurant_id (int): the restaurant id  

        Returns:
            List(RestaurantTable): a list of RestaurantTable objects, empty if None
        """
        req = safe_get(f"{Restaurant.BASE_URL}/restaurants/tables/{restaurant_id}")

        l = []
        if req.status_code == 200:
            json_dict = req.json()
            for j in json_dict["tables"]:
                r = RestaurantTable(table_id=j["table_id"], restaurant_id=restaurant_id, seats=j["seats"])
                r.invariant = j
                l.append(r)
        return l


@dataclass(eq=False, order=False)
class Review:
    """
    Review abstraction over REST endpoints.
    Do not return such instances and do not pass them around as function arguments.
    """

    reviewer_id : int
    restaurant_id : int
    stars : int
    text_review : str
    marked : bool

    invariant: dict = field(init=False, repr=False)

    @staticmethod
    def add(restaurant_id, user_id, stars, text=None):
        """Adds a new Review for the restaurant restaurant_id by the User user_id

        Args:
            restaurant_id (int): the restaurant_id
            user_id (int): the user_id
            stars (int): the number of stars
            text (str, optional): the review text if any. Defaults to None.

        Raises:
            GoOutSafeError: if a db error happens
        """
        body = {"reviewer_id":user_id, "stars":stars}
        if text:
            body['text_review'] = text
        req = safe_post(f"{Restaurant.BASE_URL}/reviews/{restaurant_id}", json=body)
        if req.status_code != 201:
            raise GoOutSafeError("DB error")

    @staticmethod
    def get(restaurant_id, user_id=None):
        """Returns all the reviews for the restaurant restaurant_id.
        If a user_id is specified it returns only that user review, if any.

        Args:
            restaurant_id (int): the restaurant id
            user_id (int, optional): the user id, if any. Defaults to None.

        Returns:
            returns a list of Review object if user_id is not specified, otherwise a single Review object.
            If nothing is found returns respectively an empty list and None.
        """
        if user_id:
            req = safe_get(f"{Restaurant.BASE_URL}/reviews/{restaurant_id}?user_id={user_id}")
            if req.status_code == 200:
                json_dict = req.json()
                if not json_dict:
                    return None
                r = Review(**json_dict[0])
                r.invariant = json_dict[0]
                return r
        else:
            req = safe_get(f"{Restaurant.BASE_URL}/reviews/{restaurant_id}")

        l = []
        if req.status_code == 200:
            json_dict = req.json()
            for j in json_dict:
                r = Review(**j)
                r.invariant = j
                l.append(r)
        return l

