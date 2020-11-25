from api_gateway.classes.user import User
from api_gateway.classes.reservations import Reservation, ReservationState
from api_gateway.classes.restaurant import Restaurant
from api_gateway.classes.user import User
from datetime import date, datetime, time
from api_gateway.app import create_app
from api_gateway.forms import ReservationForm, OperatorForm
import unittest, os, logging, random

user_data = {'email': str(random.randint(0, 1000)) + '@test.com', 
        'firstname':'Mario', 
        'lastname':'Rossi', 
        'dateofbirth': datetime(1960, 12, 3)}

clear_password = 'pass'

restaurant_data = {'name': 'Mensa martiri', 
                    'lat': '4.12345',
                    'lon': '5.67890',
                    'phone': str(random.randint(1111111111, 9999999999)),
                    'extra_info': 'Rigatoni dorati h24, cucina povera'}
data = {**user_data, **restaurant_data}

tables = {
    'table_1': 4,
    'table_2': 4,
    'table_3': 4
}

class TestReservation(unittest.TestCase):

    def setUp(self):
        try:
            self.app = create_app()
            with self.app.test_request_context():
                form = OperatorForm(**data)
                dateofbirth = datetime(form.dateofbirth.data.year, form.dateofbirth.data.month, form.dateofbirth.data.day)
                self.operator = Restaurant.create(form.email.data, \
                    form.firstname.data, form.lastname.data, \
                    'pass', dateofbirth, \
                    form.name.data, form.lat.data, form.lon.data, \
                    form.phone.data, extra_info=form.extra_info.data)
                print("OPERATOR", self.operator)
                self.assertIsNotNone(self.operator)

                Restaurant.update(self.operator.restaurant_id, tables)
                self.restaurant_id = self.operator.restaurant_id

                res_time = datetime.combine(date(datetime.today().year, datetime.today().month, datetime.today().day + 1 % 30 ), time(datetime.now().time().hour + 1 % 24, minute=00))

                self.assertIsNotNone(self.restaurant_id)
                self.reservations = [{
                    'user_id': 1,
                    'restaurant_id': self.restaurant_id,
                    'reservation_time': res_time,
                    'seats': 4
                },{
                    'user_id': 1,
                    'restaurant_id': self.restaurant_id,
                    'reservation_time': datetime.combine(datetime.today(), time(21, 00)),
                    'seats': 4
                }]

                self.reservation_ids = []     
        except Exception as e:
            print("setup failed")
    
    def tearDown(self):
        with self.app.test_request_context():
            self.assertIsNotNone(self.operator)
            Restaurant.delete(self.operator.restaurant_id)
            User.delete(self.operator.id)
            for res_id in self.reservation_ids:
                Reservation.delete_customer_reservation(res_id)

    def test_create_reservation(self):
        with self.app.test_request_context():
            for res in self.reservations:
                res_id = Reservation.new(**res)
                self.assertIsNotNone(res_id)
                self.reservation_ids.append(res_id)
            
    # def test_get_reservations(self):
    #     try:
    #         with self.app.app_context():
                
    #             r = Reservation.get_customer_reservations(1)
    #             self.assertIsNotNone(r)

    #             r = Reservation.get_paged_reservations(self.restaurant_id, 1)
    #             self.assertIsNotNone(r)

    #             r = Reservation.get_paged_reservation_of_today(self.restaurant_id, 1)
    #             self.assertIsNotNone(r)

    #             for res_id in self.reservation_ids:
    #                 r = Reservation.get_reservation(res_id)
    #                 self.assertIsNotNone(res_id)
                
    #             sc =  Reservation.get_seated_customers(self.restaurant_id)
    #             self.assertEqual(sc, 0)

    #             r = Reservation.get_reservation(-1)
    #             self.assertIsNone(r)

    #             r = Reservation.get_customer_reservations(2)
    #             self.assertEqual(len(r), 0)

    #             r, _ = Reservation.get_paged_reservation_of_today(1000, 1)
    #             self.assertEqual(len(r), 0)

    #             r, _ = Reservation.get_paged_reservations(1000, 1)
    #             self.assertEqual(len(r), 0)
    #     except Exception as e:
    #         logging.error(e)
    #         self.fail('failed')

    # def test_update(self):
    #     with self.app.app_context():
    #         new_res_time = datetime.combine(datetime.today(), time(21, 00))

    #         for res_id in self.reservation_ids:
    #             Reservation.update_customer_reservation(res_id, new_res_time, 4)
    #             Reservation.update_reservation_status(res_id, 2)

    #             r = Reservation.get_reservation(res_id)
    #             self.assertIsNotNone(r)
    
    # def test_delete_customer(self):
    #     with self.app.app_context():

    #         for res_id in self.reservation_ids:
    #             Reservation.delete_customer_reservation(res_id)
    #             r = Reservation.get_reservation(res_id)
    #             self.assertIsNone(r)


    
            










