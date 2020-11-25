from api_gateway.app import create_app
import unittest
from api_gateway.classes.notifications import fetch_notifications, get_notification_by_id
import random
from datetime import datetime
from api_gateway.classes.user import User

user_data = {'email': str(random.randint(0, 1000)) + '@test.com', 
        'firstname':'Mario', 
        'lastname':'Rossi', 
        'dateofbirth': datetime(1960, 12, 3)}
class NotificationTest(unittest.TestCase):

    def setUp(self) -> None:
        self.app = create_app()
        # create some test user
        self.user_id = User.create(**user_data, fiscal_code="aaaaaaaaaaabb", phone=str(random.randint(1111111111, 9999999999)), password="pass")
        self.user = User.get(id = self.user_id)
        # self.test_app = self.app.test_client()
    
    def tearDown(self) -> None:
        User.delete(self.user_id)

    def testFetchNotification(self):
        # test no exception raised during request
        notifs = fetch_notifications(self.user)
        self.assertIsNotNone(notifs)
        notifs = fetch_notifications(self.user, True)
        self.assertIsNotNone(notifs)

    def testFetchNotificationOperator(self):
        self.user.restaurant_id = 1
        # test no exception raised during request
        notifs = fetch_notifications(self.user)
        self.assertIsNotNone(notifs)
        notifs = fetch_notifications(self.user, True)
        self.assertIsNotNone(notifs)

    def testFetchNotificationById(self):
        # test no exception raised during request
        notifs = get_notification_by_id(1)
        self.assertIsNotNone(notifs)