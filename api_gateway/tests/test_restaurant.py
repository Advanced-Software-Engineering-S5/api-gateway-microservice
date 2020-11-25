from api_gateway.classes.user import User
from api_gateway.classes.restaurant import Restaurant, RestaurantTable, Review
from datetime import date, datetime
from api_gateway.app import create_app
from api_gateway.forms import OperatorForm, UserForm
import unittest, random

user_data = {'email': str(random.randint(0, 1000)) + '@test.com', 
        'firstname':'Mario', 
        'lastname':'Rossi', 
        'dateofbirth': date(1960, 12, 3)}

clear_password = 'pass'

restaurant_data = {'name': 'Mensa martiri', 
                    'lat': '4.12345',
                    'lon': '5.67890',
                    'phone': str(random.randint(1111111111, 9999999999)),
                    'extra_info': 'Rigatoni dorati h24, cucina povera'}
data = {**user_data, **restaurant_data}


class TestRestaurant(unittest.TestCase):
    def setUp(self) -> None:

        self.app = create_app()
        with self.app.test_request_context():
            form = OperatorForm(**data)
            dateofbirth = datetime(form.dateofbirth.data.year, form.dateofbirth.data.month, form.dateofbirth.data.day)
            self.operator = Restaurant.create(form.email.data, \
                form.firstname.data, form.lastname.data, \
                'pass', str(dateofbirth), \
                form.name.data, form.lat.data, form.lon.data, \
                form.phone.data, extra_info=form.extra_info.data)
            self.assertIsNotNone(self.operator)
            print(f"Created operator with id {self.operator.id} and r-id {self.operator.restaurant_id}")
            u = user_data.copy()
            u['email'] = str(random.randint(0, 1000)) + '@uu.com',
            form = UserForm(**u)
            # self.user = User.create(email=form.email.data, firstname=form.firstname.data, lastname=form.lastname.data, password='pass', fiscal_code="aaaaaadsaaaaaaaa", dateofbirth=datetime(1990, 12, 12))
        
    def tearDown(self) -> None:
        print(f"Deleting operator with id {self.operator.id} and r-id {self.operator.restaurant_id}")
        Restaurant.delete(self.operator.restaurant_id)
        User.delete(self.operator.id)
        # User.delete(self.user.id)
    
    def test_get(self):
        with self.app.app_context():
            r = Restaurant.get(self.operator.restaurant_id)
            self.assertIsNotNone(r)
            r.update_review(3)
            r = Restaurant.getAll()
            self.assertIsNotNone(r)
            r = Restaurant.get(-1)
            self.assertIsNone(r)


    def test_edit(self):
        # adds a new restaurant/operator and calls the "edit_tables" method on it
        # if a database error happen an SQLAlchemy exception should be raised
        # making the test fail
        tables = {"table_1":4}
        with self.app.app_context():
            Restaurant.update(self.operator.restaurant_id, tables, phone="1321123432", extra_info="test")
            r = RestaurantTable.get(self.operator.restaurant_id)
            self.assertIsNotNone(r)
            # Restaurant.get(self.operator.restaurant_id)

    def test_addreview(self):
        # adds a new restaurant/operator and and a new user and calls the
        # method "add_review" to add a review for that restaurant
        # if a database error happen an SQLAlchemy exception should be raised
        # making the test fail
        with self.app.test_request_context():
            Review.add(self.operator.restaurant_id, 10, 3, "test")
            r = Review.get(self.operator.restaurant_id)
            self.assertIsNotNone(r)
            r = Review.get(self.operator.restaurant_id, user_id=10)
            self.assertIsNotNone(r)

    def test_views(self):
        test_client = self.app.test_client()
        test_client.get('/restaurants')
        test_client.get('/restaurants/1')
        test_client.get('/restaurants/edit/1')
        test_client.get('/restaurants/reserve/1')
        test_client.post('/restaurants/1')
        test_client.post('/restaurants/edit/1')
        test_client.post('/restaurants/reserve/1')