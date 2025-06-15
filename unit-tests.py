import unittest
import json
from app import app, db, Todo, TodoList


class StarterTaskDeleteTest(unittest.TestCase):
    """Test for delete row functionality in the starter task list"""
    
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
    
    def test_starter_task_delete_row_functionality(self):
        """Test that the starter task list supports deleting individual todo items"""
        # Get the welcome page first to understand the structure
        response = self.app.get('/todos/welcome')
        self.assertEqual(response.status_code, 200)
        
        # The starter task list has dummy todos with IDs 1, 2, 3
        # We should be able to delete them using the delete endpoint
        # Even though they're dummy data, the endpoint should work
        
        # Try to delete todo with id=1 from the welcome list
        # This should work if the delete functionality is properly implemented
        response = self.app.delete('/todos/welcome/1')
        
        # If delete row feature is implemented, this should return success
        # The endpoint should handle the delete request gracefully
        self.assertEqual(response.status_code, 200)
        
        # Check that the response indicates success
        data = json.loads(response.data)
        self.assertTrue(data.get('successful', False))
    
    def test_starter_task_delete_multiple_rows(self):
        """Test deleting multiple rows from starter task list"""
        # Test deleting the second todo item
        response = self.app.delete('/todos/welcome/2')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data.get('successful', False))
        
        # Test deleting the third todo item  
        response = self.app.delete('/todos/welcome/3')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data.get('successful', False))
    
    def test_starter_task_delete_nonexistent_row(self):
        """Test deleting a row that doesn't exist in starter task"""
        # Try to delete a todo that doesn't exist
        response = self.app.delete('/todos/welcome/999')
        
        # This should either return 400 (bad request) or 200 with successful=False
        # depending on how the delete is implemented
        self.assertIn(response.status_code, [200, 400])
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # Should indicate the operation wasn't successful
            self.assertFalse(data.get('successful', True))


if __name__ == '__main__':
    # run the test
    unittest.main()