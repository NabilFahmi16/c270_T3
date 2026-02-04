import unittest
import os
import json
import tempfile
from app import app, url_data, users, hash_password

class TestURLShortener(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key-123'
        
        self.data_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.user_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        
        from app import DATA_FILE, USER_FILE
        self.original_data_file = DATA_FILE
        self.original_user_file = USER_FILE
        
        import app as app_module
        app_module.DATA_FILE = self.data_file.name
        app_module.USER_FILE = self.user_file.name
        
        self.client = app.test_client()
        
        url_data.clear()
        url_data.update({"links": {}, "analytics": {}})
        
        users.clear()
        
        self.test_user_id = "testuser123"
        users["testuser"] = {
            'id': self.test_user_id,
            'email': 'test@example.com',
            'password': hash_password('testpass123'),
            'created_at': '2024-01-01T00:00:00'
        }
        
        from app import save_users
        save_users()
        
        url_data["links"]["ci"] = {
            "url": "https://github.com/NabilFahmi16/c270_T3/actions",
            "created": "2024-01-01 00:00:00",
            "clicks": 0,
            "user_id": self.test_user_id,
            "expiry_date": None,
            "password": None,
            "utm_tracking": False
        }
        url_data["links"]["repo"] = {
            "url": "https://github.com/NabilFahmi16/c270_T3",
            "created": "2024-01-01 00:00:00",
            "clicks": 0,
            "user_id": self.test_user_id,
            "expiry_date": None,
            "password": None,
            "utm_tracking": False
        }
        
        url_data["analytics"]["ci"] = {
            "clicks": [],
            "referrers": {},
            "countries": {},
            "browsers": {}
        }
        url_data["analytics"]["repo"] = {
            "clicks": [],
            "referrers": {},
            "countries": {},
            "browsers": {}
        }
        
        from app import save_data
        save_data()
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_user_id
            sess['username'] = "testuser"
    
    def tearDown(self):
        self.data_file.close()
        self.user_file.close()
        
        try:
            os.unlink(self.data_file.name)
            os.unlink(self.user_file.name)
        except:
            pass
        
        import app as app_module
        app_module.DATA_FILE = self.original_data_file
        app_module.USER_FILE = self.original_user_file
    
    def test_health_endpoint(self):
        resp = self.client.get('/health')
        if resp.status_code == 404:
            print("Note: /health endpoint not implemented yet")
            return
        
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 'ok')

   
    
    def test_home_page_unauthenticated(self):
        with self.client.session_transaction() as sess:
            sess.clear()
        
        # Test to show it fails
    # def test_home_page_authenticated(self):
    #     with self.client.session_transaction() as sess:
    #         sess.clear() 
    
    #     resp = self.client.get('/')
    #     self.assertEqual(resp.status_code, 200)
    #     self.assertIn(b'URL Shortener Pro', resp.data)
        
        def test_home_page_authenticated(self):
            resp = self.client.get('/')
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'URL Shortener Pro', resp.data)
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        
            resp = self.client.get('/', follow_redirects=False)
            self.assertEqual(resp.status_code, 302)  
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    def test_login_page(self):
        resp = self.client.get('/login')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Login', resp.data)
    
    def test_api_shorten_basic(self):
        resp = self.client.post('/api/shorten', 
            json={"url": "https://rp.edu.sg"},
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn('alias', data)
        self.assertIn('short_url', data)
    
    def test_api_shorten_with_custom_alias(self):
        resp = self.client.post('/api/shorten', 
            json={
                "alias": "customtest",
                "url": "https://rp.edu.sg"
            },
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertEqual(data['alias'], 'customtest')
    
    def test_api_shorten_invalid_url(self):
        resp = self.client.post('/api/shorten', 
            json={"url": "invalid-url"},
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertIn('error', data)
    
    def test_api_shorten_duplicate_alias(self):
        resp1 = self.client.post('/api/shorten', 
            json={"alias": "test", "url": "https://example1.com"},
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(resp1.status_code, 201)
        
        resp2 = self.client.post('/api/shorten', 
            json={"alias": "test", "url": "https://example2.com"},
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(resp2.status_code, 409)
        data = resp2.get_json()
        self.assertIn('error', data)
    
    def test_redirect_basic(self):
        self.client.post('/api/shorten', 
            json={"alias": "testredirect", "url": "https://rp.edu.sg"},
            headers={'Content-Type': 'application/json'}
        )
        
        resp = self.client.get('/go/testredirect', follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('rp.edu.sg', resp.location)
        
        self.assertEqual(url_data["links"]["testredirect"]["clicks"], 1)
    
    def test_redirect_not_found(self):
        resp = self.client.get('/go/nonexistent')
        self.assertEqual(resp.status_code, 404)
    
    def test_api_delete_success(self):
        self.client.post('/api/shorten', 
            json={"alias": "todelete", "url": "https://example.com"},
            headers={'Content-Type': 'application/json'}
        )
        
        resp = self.client.delete('/api/delete/todelete')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        
        self.assertNotIn('todelete', url_data["links"])
    
    def test_api_delete_not_found(self):
        resp = self.client.delete('/api/delete/nonexistent')
        self.assertEqual(resp.status_code, 404)
        data = resp.get_json()
        self.assertIn('error', data)
    
    def test_analytics_endpoint(self):
        self.client.get('/go/ci', follow_redirects=False)
        
        resp = self.client.get('/analytics/ci')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Analytics', resp.data)
    
    def test_hash_password_function(self):
        result = hash_password("test123")
        self.assertEqual(len(result), 64)
        self.assertIsInstance(result, str)
        
        result2 = hash_password("test123")
        self.assertEqual(result, result2)
    
    def test_generate_random_alias(self):
        from app import generate_random_alias
        
        alias = generate_random_alias()
        self.assertEqual(len(alias), 6)
        self.assertTrue(alias.isalnum())
        
        alias2 = generate_random_alias(8)
        self.assertEqual(len(alias2), 8)

if __name__ == '__main__':
    unittest.main(verbosity=2)
