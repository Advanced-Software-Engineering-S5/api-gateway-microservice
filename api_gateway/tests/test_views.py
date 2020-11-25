import unittest
from api_gateway.app import create_app

class TestViews(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.test = self.app.test_client()

    def test_views(self):
        self.test.get('/')
        self.test.get('/signup')
        self.test.get('/login')
        self.test.get('/logout')
        self.test.get('/unregister/-1')
        self.test.post('/login')