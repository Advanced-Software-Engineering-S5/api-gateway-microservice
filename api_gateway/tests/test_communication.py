import unittest
import requests
import os

# checks whether communications work as intended, meant for both
# production and development environment
class CommunicationTest(unittest.TestCase):

    def test_user_communication(self):
        print("request to", f"http://{os.environ.get('GOS_USER')}/")
        
        res = requests.get(f"http://{os.environ.get('GOS_USER')}/")
        print(res)
        self.assertIsNotNone(res)

    def test_reservation_communication(self):
        print("request to", f"http://{os.environ.get('GOS_RESERVATION')}/")
        
        res = requests.get(f"http://{os.environ.get('GOS_RESERVATION')}/")
        self.assertIsNotNone(res)

    def test_restaurant_communication(self):
        print("request to", f"http://{os.environ.get('GOS_RESTAURANT')}/")
        
        res = requests.get(f"http://{os.environ.get('GOS_RESTAURANT')}/")
        self.assertIsNotNone(res)

    def test_notification_communication(self):
        print("request to", f"http://{os.environ.get('GOS_NOTIFICATION')}/")
        
        res = requests.get(f"http://{os.environ.get('GOS_NOTIFICATION')}/")
        self.assertIsNotNone(res)