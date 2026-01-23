# test_app.py (BASIC)
import unittest
from app import app

class TestBasic(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health(self):
        resp = self.client.get('/health')
        self.assertEqual(resp.status_code, 200)

    def test_shorten(self):
        resp = self.client.post('/shorten', json={"alias": "test", "url": "https://rp.edu.sg"})
        self.assertEqual(resp.status_code, 201)

if __name__ == '__main__':
    unittest.main()