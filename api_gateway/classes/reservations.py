from api_gateway.classes.utils import safe_get, safe_post, safe_put, safe_delete
from dataclasses import dataclass, field, fields
from datetime import datetime, time
from typing import Optional
import os
import enum

def try_fromisoformat(iso):
    if type(iso) == str:
        try:
            return datetime.fromisoformat(iso)
        except ValueError:
            pass
    return None

class ReservationState(enum.IntEnum):
    DECLINED = 0
    PENDING = 1
    ACCEPTED = 2
    SEATED = 3
    DONE = 4

    def __str__(self):
        return {
            self.DECLINED: "Declined",
            self.PENDING: "Pending",
            self.ACCEPTED: "Accepted",
            self.SEATED: "Seated",
            self.DONE: "Done"
        }.get(self)

@dataclass
class Reservation:
    """ 
     Reservation abstraction over REST endpoints.
    """

    BASE_URL = f'http://{os.environ.get("GOS_RESERVATION")}'

    id: int
    user_id: int
    restaurant_id: int
    reservation_time: datetime
    table_no: int
    seats: int
    status: ReservationState = ReservationState.PENDING
    entrance_time: datetime = None
    exit_time: datetime = None

    invariant: dict = field(init=False, repr=False)

    ### CUSTOMER RESERVATIONS ###

    @staticmethod
    def get_customer_reservations(user_id: int):
        """ 
        Returns a list of future reservations (empty list if no reservations were found) made by the user specified by the given user_id.
        """
        reservations = []
        url = f'{Reservation.BASE_URL}/customer_reservations/{user_id}'
        try:
            req = safe_get(url=url)
            if req.status_code == 200:
                body = req.json()['reservations']
                for res_json in body:
                    res_json['reservation_time'] = try_fromisoformat(res_json['reservation_time'])
                    res_json['entrance_time'] = try_fromisoformat(res_json['entrance_time'])
                    res_json['exit_time'] = try_fromisoformat(res_json['exit_time'])

                    res = Reservation(**res_json)
                    res.invariant = res_json
                    reservations.append(res)
                    return reservations
            else:
                return reservations   
        except Exception as e:
            return reservations

    @staticmethod
    def new(user_id: int, restaurant_id: int, reservation_time: datetime, seats: int):
        """
        Adds a new  reservation.
         """
        body = {}
        body['user_id'] = user_id
        body['restaurant_id'] = restaurant_id
        body['reservation_time'] = datetime.isoformat(reservation_time)
        body['seats'] = seats
        url = f'{Reservation.BASE_URL}/reserve'
        try:  
            req = safe_post(url=url, json=body)
            print(req.json())
            if req.status_code == 200:
                return 'Reservation added correctly'
            else:
                return req.json()['message']
        except Exception as e:
            print(e)
            return 'Reservation service not reachable'    
    
    @staticmethod
    def update_customer_reservation(reservation_id: int, new_reservation_time: datetime, new_seats: int):
        body = {}
        body['new_reservation_time'] = datetime.isoformat(new_reservation_time)
        body['new_seats'] = new_seats

        url = f'{Reservation.BASE_URL}/customer_reservation/{reservation_id}'
        try:
            req = safe_put(url=url, json=body)
            print(req)
            return req.json()['message']
        except Exception as e:
            return 'Reservation service not reachable'
    

    @staticmethod
    def delete_customer_reservation(reservation_id: int):

        url = f'{Reservation.BASE_URL}/customer_reservation/{reservation_id}'

        try:
            req = safe_delete(url=url)
            return req.json()['message']
        except Exception as e:
            'Reservation service not reachable'

    ### OPERATOR RESERVATIONS ###
    
    @staticmethod
    def update_reservation_status(reservation_id: int, status: int, time=None):
        body = {}
        body['status'] = status
        body['time'] = time
        url = f'{Reservation.BASE_URL}/reservation/{reservation_id}/status'
        try: 
            req = safe_put(url=url, json=body)
            return req.json()['message']
        except:
            'Reservation service not reachable'
    
    @staticmethod
    def get_paged_reservations(restaurant_id: int, page: int):
        reservations = []
        url = f'{Reservation.BASE_URL}/reservations/{restaurant_id}?page={page}'
        try:
            req = safe_get(url=url)
            if req.status_code == 200:
                for res_json in req.json():
                    res_json['reservation_time'] = try_fromisoformat(res_json['reservation_time'])
                    res_json['entrance_time'] = try_fromisoformat(res_json['entrance_time'])
                    res_json['exit_time'] = try_fromisoformat(res_json['exit_time'])
                    res = Reservation(**res_json)
                    res.invariant = res_json
                    reservations.append(res)
                    return reservations
            else:
                return reservations   
        except Exception as e:
            return reservations
    
    @staticmethod
    def get_seated_customers(restaurant_id: int):
        reservations = []
        url = f'{Reservation.BASE_URL}/reservations/{restaurant_id}?seated=True'
        try:
            req = safe_get(url=url)
            if req.status_code == 200:
                for res_json in req.json():
                    res_json['reservation_time'] = try_fromisoformat(res_json['reservation_time'])
                    res_json['entrance_time'] = try_fromisoformat(res_json['entrance_time'])
                    res_json['exit_time'] = try_fromisoformat(res_json['exit_time'])
                    res = Reservation(**res_json)
                    res.invariant = res_json
                    reservations.append(res)
                    return reservations
            else:
                return reservations   
        except Exception as e:
            return reservations

class ReservationState(enum.IntEnum):
    DECLINED = 0
    PENDING = 1
    ACCEPTED = 2
    SEATED = 3
    DONE = 4

    def __str__(self):
        return {
            self.DECLINED: "Declined",
            self.PENDING: "Pending",
            self.ACCEPTED: "Accepted",
            self.SEATED: "Seated",
            self.DONE: "Done"
        }.get(self)


            

                

        




