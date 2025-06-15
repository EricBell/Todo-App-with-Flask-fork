import unittest
import json
from app import app, db


class StarterTaskDeleteFeatureTest(unittest.TestCase):
    """Test that delete feature actually works and persists during session"""
    
    def setUp(self):
        """setup before each test"""
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        # Clear any previously deleted tasks for clean test
        if hasattr(app, 'deleted_starter_tasks'):
            app.deleted_starter_tasks.clear()
        
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """cleanup after test"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_delete_task_actually_removes_from_list(self):
        """Test that deleting a task actually removes it from the starter list"""
        # First, get the starter task list to see all 3 tasks
        response = self.app.get('/todos/welcome')
        self.assertEqual(response.status_code, 200)
        
        # Should contain all 3 tasks initially
        self.assertIn(b'<li id="_1">', response.data)
        self.assertIn(b'<li id="_2">', response.data) 
        self.assertIn(b'<li id="_3">', response.data)
        
        # Delete task with id=1
        delete_response = self.app.delete('/todos/welcome/1')
        self.assertEqual(delete_response.status_code, 200)
        
        data = json.loads(delete_response.data)
        self.assertTrue(data.get('successful', False))
        
        # Now get the list again - task 1 should be gone!
        response_after_delete = self.app.get('/todos/welcome')
        self.assertEqual(response_after_delete.status_code, 200)
        
        # Check that task 1 is no longer in the todos section
        self.assertNotIn(b'<li id="_1">', response_after_delete.data)
        # But tasks 2 and 3 should still be there
        self.assertIn(b'<li id="_2">', response_after_delete.data)
        self.assertIn(b'<li id="_3">', response_after_delete.data)
    
    def test_delete_multiple_tasks_persist(self):
        """Test that multiple deletions persist in the session"""
        # Delete tasks 1 and 2
        response1 = self.app.delete('/todos/welcome/1')
        self.assertEqual(response1.status_code, 200)
        
        response2 = self.app.delete('/todos/welcome/2')  
        self.assertEqual(response2.status_code, 200)
        
        # Get the list - should only show task 3
        list_response = self.app.get('/todos/welcome')
        self.assertEqual(list_response.status_code, 200)
        
        # Should not contain deleted task elements
        self.assertNotIn(b'<li id="_1">', list_response.data)  # task 1
        self.assertNotIn(b'<li id="_2">', list_response.data)  # task 2
        # Should still contain task 3
        self.assertIn(b'<li id="_3">', list_response.data)  # task 3
    
    def test_delete_all_tasks_shows_empty_list(self):
        """Test deleting all starter tasks results in empty list"""
        # Delete all 3 tasks
        for task_id in [1, 2, 3]:
            response = self.app.delete(f'/todos/welcome/{task_id}')
            self.assertEqual(response.status_code, 200)
        
        # Get the list - should be empty or show no tasks
        list_response = self.app.get('/todos/welcome')
        self.assertEqual(list_response.status_code, 200)
        
        # None of the task elements should appear
        self.assertNotIn(b'<li id="_1">', list_response.data)
        self.assertNotIn(b'<li id="_2">', list_response.data) 
        self.assertNotIn(b'<li id="_3">', list_response.data)
    
    def test_deletion_persists_across_multiple_requests(self):
        """Test that deletion persists across multiple GET requests in same session"""
        # Delete task 2
        delete_response = self.app.delete('/todos/welcome/2')
        self.assertEqual(delete_response.status_code, 200)
        
        # Make multiple GET requests - deletion should persist
        for i in range(3):
            list_response = self.app.get('/todos/welcome')
            self.assertEqual(list_response.status_code, 200)
            # Task 2 should still be missing
            self.assertNotIn(b'<li id="_2">', list_response.data)
            # But tasks 1 and 3 should still be there
            self.assertIn(b'<li id="_1">', list_response.data)
            self.assertIn(b'<li id="_3">', list_response.data)


if __name__ == '__main__':
    unittest.main()