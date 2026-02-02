import unittest
from app import app, url_map

class TestBasic(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        # Clear url_map before each test (except default entries)
        url_map.clear()
        url_map["ci"] = {
            "url": "https://github.com/NabilFahmi16/c270_T3/actions",
            "created": "2024-01-01 00:00:00",
            "clicks": 0
        }
        url_map["repo"] = {
            "url": "https://github.com/NabilFahmi16/c270_T3",
            "created": "2024-01-01 00:00:00",
            "clicks": 0
        }
    
    def test_health(self):
        resp = self.client.get('/health')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 'ok')
    
    def test_shorten(self):
        resp = self.client.post('/shorten', json={"alias": "test", "url": "https://rp.edu.sg"})
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn('message', data)
        self.assertEqual(data['alias'], 'test')
    
    def test_shorten_missing_data(self):
        resp = self.client.post('/shorten', json={"alias": "test"})
        self.assertEqual(resp.status_code, 400)
    
    def test_shorten_duplicate_alias(self):
        self.client.post('/shorten', json={"alias": "test", "url": "https://rp.edu.sg"})
        resp = self.client.post('/shorten', json={"alias": "test", "url": "https://example.com"})
        self.assertEqual(resp.status_code, 409)
    
    def test_redirect(self):
        self.client.post('/shorten', json={"alias": "test", "url": "https://rp.edu.sg"})
        resp = self.client.get('/go/test', follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, 'https://rp.edu.sg')
    
    def test_redirect_not_found(self):
        resp = self.client.get('/go/nonexistent')
        self.assertEqual(resp.status_code, 404)
    
    def test_list_links(self):
        resp = self.client.get('/links')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIsInstance(data, dict)

if __name__ == '__main__':
    unittest.main()
