import unittest
import json
import os
from datetime import datetime, timedelta
from flask import Flask, session
from app import app, url_data, users, save_data, save_users, load_data, load_users
from app import generate_random_alias, hash_password, is_expired

# For testing we use in-memory structures + temp files
TEST_DATA_FILE = "test_urls.json"
TEST_USER_FILE = "test_users.json"


class TestURLShortener(unittest.TestCase):
    def setUp(self):
        # Use test files instead of real ones
        app.config['TESTING'] = True
        self.client = app.test_client()

        # Backup original files (if exist)
        self.original_data_file = app.root_path + "/../" + "urls.json"
        self.original_user_file = app.root_path + "/../" + "users.json"

        # Override file paths for tests
        global DATA_FILE, USER_FILE
        DATA_FILE = TEST_DATA_FILE
        USER_FILE = TEST_USER_FILE

        # Clean up any previous test files
        for f in [TEST_DATA_FILE, TEST_USER_FILE]:
            if os.path.exists(f):
                os.remove(f)

        # Reset global data
        global url_data, users
        url_data = load_data()
        users = load_users()

    def tearDown(self):
        # Clean up test files
        for f in [TEST_DATA_FILE, TEST_USER_FILE]:
            if os.path.exists(f):
                os.remove(f)

    # ────────────────────────────────────────────────
    # Persistence tests
    # ────────────────────────────────────────────────
    def test_load_nonexistent_files(self):
        data = load_data()
        users_data = load_users()
        self.assertEqual(data, {"links": {}, "analytics": {}})
        self.assertEqual(users_data, {})

    def test_save_and_load_data(self):
        url_data["links"]["test123"] = {"url": "https://example.com", "clicks": 5}
        url_data["analytics"]["test123"] = {"clicks": []}
        save_data()

        loaded = load_data()
        self.assertIn("test123", loaded["links"])
        self.assertEqual(loaded["links"]["test123"]["url"], "https://example.com")
        self.assertEqual(loaded["links"]["test123"]["clicks"], 5)

    def test_save_and_load_users(self):
        users["testuser"] = {
            "id": "abc123",
            "email": "test@example.com",
            "password": hash_password("pass123"),
        }
        save_users()

        loaded = load_users()
        self.assertIn("testuser", loaded)
        self.assertEqual(loaded["testuser"]["email"], "test@example.com")

    # ────────────────────────────────────────────────
    # Authentication
    # ────────────────────────────────────────────────
    def _login(self, username="testuser", password="pass123"):
        # First register if needed
        if username not in users:
            self.client.post('/register', data={
                'username': username,
                'email': f'{username}@example.com',
                'password': password
            }, follow_redirects=True)

        resp = self.client.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)
        return resp

    def test_register_and_login(self):
        resp = self.client.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'secret123'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'URL Shortener Pro v2.0', resp.data)

        # Logout
        self.client.get('/logout', follow_redirects=True)

        # Login again
        resp = self.client.post('/login', data={
            'username': 'newuser',
            'password': 'secret123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome, <strong>newuser</strong>', resp.data)

    def test_invalid_login(self):
        resp = self.client.post('/login', data={
            'username': 'nonexistent',
            'password': 'wrong'
        }, follow_redirects=True)
        self.assertIn(b'Invalid credentials', resp.data.decode('utf-8'))

    # ────────────────────────────────────────────────
    # Shorten & Redirect
    # ────────────────────────────────────────────────
    def test_create_short_link_auto_alias(self):
        self._login()
        resp = self.client.post('/api/shorten', json={
            'url': 'https://example.com/very/long/url'
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        alias = data['alias']
        self.assertTrue(len(alias) >= 6)
        self.assertIn('short_url', data)

    def test_create_short_link_custom_alias(self):
        self._login()
        resp = self.client.post('/api/shorten', json={
            'url': 'https://rp.edu.sg',
            'alias': 'rp'
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertEqual(data['alias'], 'rp')

    def test_duplicate_alias_rejected(self):
        self._login()
        self.client.post('/api/shorten', json={
            'url': 'https://example.com',
            'alias': 'duplicate'
        })
        resp = self.client.post('/api/shorten', json={
            'url': 'https://other.com',
            'alias': 'duplicate'
        })
        self.assertEqual(resp.status_code, 409)

    def test_redirect_works(self):
        self._login()
        shorten_resp = self.client.post('/api/shorten', json={
            'url': 'https://google.com'
        })
        alias = shorten_resp.get_json()['alias']

        resp = self.client.get(f'/go/{alias}', follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, 'https://google.com')

    def test_redirect_not_found(self):
        resp = self.client.get('/go/thisdoesnotexist999')
        self.assertEqual(resp.status_code, 404)

    # ────────────────────────────────────────────────
    # Delete
    # ────────────────────────────────────────────────
    def test_delete_own_link(self):
        self._login('owner')
        shorten = self.client.post('/api/shorten', json={
            'url': 'https://delete.me'
        })
        alias = shorten.get_json()['alias']

        resp = self.client.delete(f'/api/delete/{alias}')
        self.assertEqual(resp.status_code, 200)

        # Check it's gone
        resp = self.client.get(f'/go/{alias}')
        self.assertEqual(resp.status_code, 404)

    # ────────────────────────────────────────────────
    # Expiry (basic)
    # ────────────────────────────────────────────────
    def test_expired_link(self):
        self._login()
        past = (datetime.now() - timedelta(days=1)).isoformat()
        url_data["links"]["expired"] = {
            "url": "https://expired.com",
            "expiry_date": past,
            "clicks": 0,
            "user_id": session['user_id']
        }
        save_data()

        resp = self.client.get('/go/expired')
        self.assertEqual(resp.status_code, 410)
        self.assertIn(b'This link has expired', resp.data)

    # Add more tests as needed (analytics, password protection, etc.)


if __name__ == '__main__':
    unittest.main()
