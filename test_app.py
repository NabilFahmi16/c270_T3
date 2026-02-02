import unittest
import os
import tempfile
from app import app, load_data, save_data, load_users, save_users

class TestConfiguration(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.test_dir, 'test_urls.json')
        self.users_file = os.path.join(self.test_dir, 'test_users.json')
        
        # Temporarily override file paths
        app.config['DATA_FILE'] = self.data_file
        app.config['USER_FILE'] = self.users_file
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_load_nonexistent_data_file(self):
        """Test loading when data file doesn't exist"""
        data = load_data()
        self.assertEqual(data, {})
    
    def test_load_nonexistent_users_file(self):
        """Test loading when users file doesn't exist"""
        users = load_users()
        self.assertEqual(users, {})
    
    def test_save_and_load_data(self):
        """Test round-trip data persistence"""
        test_data = {
            "links": {
                "test": {
                    "url": "https://example.com",
                    "created": "2024-01-01 00:00:00",
                    "clicks": 10
                }
            },
            "analytics": {}
        }
        
        # Save
        global url_data
        from app import url_data
        url_data = test_data
        save_data()
        
        # Verify file exists
        self.assertTrue(os.path.exists(self.data_file))
        
        # Load and verify
        loaded = load_data()
        self.assertEqual(loaded["links"]["test"]["url"], "https://example.com")
        self.assertEqual(loaded["links"]["test"]["clicks"], 10)
    
    def test_save_and_load_users(self):
        """Test round-trip user persistence"""
        test_users = {
            "user1": {
                "id": "123",
                "email": "user1@example.com",
                "password": "hashedpass",
                "created_at": "2024-01-01T00:00:00"
            }
        }
        
        # Save
        global users
        from app import users
        users = test_users
        save_users()
        
        # Verify file exists
        self.assertTrue(os.path.exists(self.users_file))
        
        # Load and verify
        loaded = load_users()
        self.assertEqual(loaded["user1"]["email"], "user1@example.com")
        self.assertEqual(loaded["user1"]["id"], "123")
    
    def test_json_file_corruption(self):
        """Test handling of corrupted JSON files"""
        # Create corrupted JSON file
        with open(self.data_file, 'w') as f:
            f.write('{invalid json}')
        
        # Should return empty dict when corrupted
        data = load_data()
        self.assertEqual(data, {})
        
        # Same for users file
        with open(self.users_file, 'w') as f:
            f.write('{invalid json}')
        
        users = load_users()
        self.assertEqual(users, {})

if __name__ == '__main__':
    unittest.main()
