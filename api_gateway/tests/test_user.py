from api_gateway.classes.user import User, edit_user_data
from datetime import datetime
from api_gateway.app import create_app
from api_gateway.forms import UserProfileEditForm
import unittest, random

user_data = {'email': str(random.randint(0, 1000)) + '@test.com', 
        'firstname':'Mario', 
        'lastname':'Rossi', 
        'dateofbirth': datetime(1960, 12, 3)}

class TestUser(unittest.TestCase):
    def setUp(self) -> None:

        self.app = create_app()
        with self.app.test_request_context():
            self.user_id = User.create(**user_data, fiscal_code="aaaaaaaaaaaaa", phone=str(random.randint(1111111111, 9999999999)), password="pass")
            self.assertIsNotNone(self.user_id)
            
            # self.user = User.create(email=form.email.data, firstname=form.firstname.data, lastname=form.lastname.data, password='pass', fiscal_code="aaaaaadsaaaaaaaa", dateofbirth=datetime(1990, 12, 12))
    
    def tearDown(self) -> None:
        with self.app.test_request_context():
            User.delete(self.user_id)

    def test_create(self):
        with self.app.test_request_context():
            u = User.get(id=self.user_id)
            self.assertIsNotNone(u)

    def test_edit(self):
        with self.app.test_request_context():
            form = UserProfileEditForm()
            edit_user_data(self.user_id, form)


    def test_get(self):
        with self.app.test_request_context():
            all = User.all()
            self.assertIsNotNone(all)
            u = User.filter("and_(User.id > 1, User.id < 3)")
            self.assertIsNotNone(u)
            u = User.filter("and_(User.id < -1, User.id < -3)")
            self.assertIsNone(u)
            u = User.get(id=-1)
            self.assertIsNone(u)


    def test_views(self):
        test_client = self.app.test_client()
        test_client.get('/users')
        test_client.get('/create_user')
        test_client.get('/create_operator')
        test_client.get('/users/edit/1')
        test_client.get('/notifications')
        test_client.get('/notifications/1')
        test_client.post('/create_user')
        test_client.post('/create_operator')
        test_client.post('/users/edit/1')
