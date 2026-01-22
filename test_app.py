# test_app.py
import unittest
from app import app

class TestURLShortener(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn("C270 DevOps URL Shortener", response.get_json()["message"])

    def test_health(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "healthy")

    def test_list_links(self):
        response = self.client.get('/links')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("ci", data)

    def test_shorten_valid(self):
        payload = {"alias": "rp", "url": "https://www.rp.edu.sg"}
        response = self.client.post('/shorten', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn("short_url", response.get_json())

    def test_shorten_invalid_no_alias(self):
        response = self.client.post('/shorten', json={"url": "https://example.com"})
        self.assertEqual(response.status_code, 400)

    def test_shorten_invalid_url(self):
        response = self.client.post('/shorten', json={"alias": "bad", "url": "not-a-url"})
        self.assertEqual(response.status_code, 400)

    def test_redirect_valid(self):
        response = self.client.get('/go/ci', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.startswith("http"))

    def test_redirect_invalid(self):
        response = self.client.get('/go/doesnotexist')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()