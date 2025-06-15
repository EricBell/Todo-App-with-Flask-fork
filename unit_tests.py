import unittest
import json
from app import app, db


class StarterTaskDeleteFeatureTest(unittest.TestCase):
    """Test specifically for delete row functionality in the starter task list"""
    
    def setUp(self):
        """setup before each test"""
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """cleanup after test"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_delete_starter_task_row(self):
        """Test that we can delete a row from the starter task list"""
        # The starter task has dummy todos with IDs 1, 2, 3
        # Try to delete todo with id=1 from the welcome list
        response = self.app.delete('/todos/welcome/1')
        
        # Should return 200 if delete feature is implemented
        self.assertEqual(response.status_code, 200)
        
        # Response should indicate success
        data = json.loads(response.data)
        self.assertTrue(data.get('successful', False))
    
    def test_delete_all_starter_task_rows(self):
        """Test deleting all rows from starter task list one by one"""
        # Delete each of the 3 starter todos
        for todo_id in [1, 2, 3]:
            response = self.app.delete(f'/todos/welcome/{todo_id}')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertTrue(data.get('successful', False))


if __name__ == '__main__':
    unittest.main()