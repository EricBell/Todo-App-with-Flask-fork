'''
  1. Basic deletion test - Verifies a deleted list is removed from database
  2. Cascade deletion test - Verifies associated todos are also deleted (expected behavior)
  3. Non-existent list test - Handles deletion attempts on non-existent lists
  4. Success response test - Checks proper JSON response format
  5. Multiple deletions test - Ensures multiple lists can be deleted and stay deleted
  6. Persistence test - Confirms deleted lists remain deleted even after other operations
'''
import unittest
import json
from app import app, db, Todo, TodoList


class TodoListDeletionTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment before each test"""
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up after each test"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_delete_list_removes_from_database(self):
        """Test that deleting a list removes it from the database"""
        # Create a test list
        with app.app_context():
            test_list = TodoList(name='Test List to Delete')
            db.session.add(test_list)
            db.session.commit()
            list_id = test_list.id
        
        # Verify list exists before deletion
        with app.app_context():
            existing_list = db.session.get(TodoList, list_id)
            self.assertIsNotNone(existing_list)
            self.assertEqual(existing_list.name, 'Test List to Delete')
        
        # Delete the list
        response = self.app.delete(f'/todos/{list_id}')
        self.assertEqual(response.status_code, 200)
        
        # Verify list is deleted and stays deleted
        with app.app_context():
            deleted_list = db.session.get(TodoList, list_id)
            self.assertIsNone(deleted_list)
    
    def test_delete_list_with_todos_removes_both(self):
        """Test that deleting a list also deletes all associated todos"""
        # Create a test list with todos
        with app.app_context():
            test_list = TodoList(name='List with Todos')
            db.session.add(test_list)
            db.session.commit()
            list_id = test_list.id
            
            # Add todos to the list
            todo1 = Todo(description='Todo 1', todolist_id=list_id)
            todo2 = Todo(description='Todo 2', todolist_id=list_id, completed=True)
            db.session.add(todo1)
            db.session.add(todo2)
            db.session.commit()
            todo1_id = todo1.id
            todo2_id = todo2.id
        
        # Verify list and todos exist before deletion
        with app.app_context():
            existing_list = db.session.get(TodoList, list_id)
            existing_todo1 = db.session.get(Todo, todo1_id)
            existing_todo2 = db.session.get(Todo, todo2_id)
            self.assertIsNotNone(existing_list)
            self.assertIsNotNone(existing_todo1)
            self.assertIsNotNone(existing_todo2)
        
        # Delete the list
        response = self.app.delete(f'/todos/{list_id}')
        self.assertEqual(response.status_code, 200)
        
        # Verify list and all todos are deleted and stay deleted (expected behavior)
        with app.app_context():
            deleted_list = db.session.get(TodoList, list_id)
            deleted_todo1 = db.session.get(Todo, todo1_id)
            deleted_todo2 = db.session.get(Todo, todo2_id)
            self.assertIsNone(deleted_list)
            # These should be None when cascade deletion works properly
            self.assertIsNone(deleted_todo1)
            self.assertIsNone(deleted_todo2)
    
    def test_delete_nonexistent_list_returns_success(self):
        """Test that deleting a non-existent list returns success (no-op)"""
        # Try to delete a list that doesn't exist
        response = self.app.delete('/todos/999')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['successful'])
    
    def test_delete_list_returns_success_response(self):
        """Test that successful deletion returns proper JSON response"""
        # Create a test list
        with app.app_context():
            test_list = TodoList(name='List for Success Test')
            db.session.add(test_list)
            db.session.commit()
            list_id = test_list.id
        
        # Delete the list
        response = self.app.delete(f'/todos/{list_id}')
        self.assertEqual(response.status_code, 200)
        
        # Check response format
        data = json.loads(response.data)
        self.assertTrue('successful' in data)
        self.assertTrue(data['successful'])
    
    def test_multiple_deletions_stay_deleted(self):
        """Test that multiple lists can be deleted and all stay deleted"""
        list_ids = []
        
        # Create multiple test lists
        with app.app_context():
            for i in range(3):
                test_list = TodoList(name=f'Test List {i+1}')
                db.session.add(test_list)
                db.session.commit()
                list_ids.append(test_list.id)
        
        # Verify all lists exist
        with app.app_context():
            for list_id in list_ids:
                existing_list = db.session.get(TodoList, list_id)
                self.assertIsNotNone(existing_list)
        
        # Delete all lists
        for list_id in list_ids:
            response = self.app.delete(f'/todos/{list_id}')
            self.assertEqual(response.status_code, 200)
        
        # Verify all lists are deleted and stay deleted
        with app.app_context():
            for list_id in list_ids:
                deleted_list = db.session.get(TodoList, list_id)
                self.assertIsNone(deleted_list)
    
    def test_delete_list_persistence_across_operations(self):
        """Test that deleted lists remain deleted even after other database operations"""
        # Create test lists
        with app.app_context():
            list_to_delete = TodoList(name='List to Delete')
            list_to_keep = TodoList(name='List to Keep')
            db.session.add(list_to_delete)
            db.session.add(list_to_keep)
            db.session.commit()
            delete_id = list_to_delete.id
            keep_id = list_to_keep.id
        
        # Delete one list
        response = self.app.delete(f'/todos/{delete_id}')
        self.assertEqual(response.status_code, 200)
        
        # Perform other operations (create new list, modify existing)
        new_list_data = {'name': 'New List After Deletion'}
        self.app.post('/todos', 
                     data=json.dumps(new_list_data),
                     content_type='application/json')
        
        # Verify deleted list is still gone and other list still exists
        with app.app_context():
            deleted_list = db.session.get(TodoList, delete_id)
            kept_list = db.session.get(TodoList, keep_id)
            self.assertIsNone(deleted_list)
            self.assertIsNotNone(kept_list)
            self.assertEqual(kept_list.name, 'List to Keep')
    
    def test_delete_list_persists_after_page_refresh(self):
        """Test that deleted lists stay deleted after page refresh (simulated by GET requests)"""
        # Create multiple test lists
        with app.app_context():
            list1 = TodoList(name='Keep This List')
            list2 = TodoList(name='Delete This List')
            list3 = TodoList(name='Another Keep List')
            db.session.add(list1)
            db.session.add(list2)
            db.session.add(list3)
            db.session.commit()
            keep1_id = list1.id
            delete_id = list2.id
            keep2_id = list3.id
        
        # Simulate initial page load - get all lists (what left sidebar would show)
        response = self.app.get('/')
        self.assertIn(response.status_code, [200, 302])  # Either shows page or redirects
        
        # Delete one of the lists (simulating user clicking delete on left sidebar)
        delete_response = self.app.delete(f'/todos/{delete_id}')
        self.assertEqual(delete_response.status_code, 200)
        
        # Simulate page refresh by making GET requests to various endpoints
        # Test home page refresh
        home_response = self.app.get('/')
        self.assertIn(home_response.status_code, [200, 302])
        
        # Test accessing the remaining lists (what would be shown in left sidebar)
        list1_response = self.app.get(f'/todos/{keep1_id}')
        self.assertEqual(list1_response.status_code, 200)
        
        list3_response = self.app.get(f'/todos/{keep2_id}')
        self.assertEqual(list3_response.status_code, 200)
        
        # Test that accessing the deleted list fails appropriately
        # This should fail because the list no longer exists
        try:
            deleted_list_response = self.app.get(f'/todos/{delete_id}')
            # If we get here, check that it's an error status
            self.assertIn(deleted_list_response.status_code, [404, 500, 302])
        except Exception:
            # Exception is expected when trying to access deleted list
            # This indicates the list is truly deleted and can't be accessed
            pass
        
        # Verify in database that the list is still deleted after all these requests
        with app.app_context():
            deleted_list = db.session.get(TodoList, delete_id)
            kept_list1 = db.session.get(TodoList, keep1_id)
            kept_list2 = db.session.get(TodoList, keep2_id)
            
            self.assertIsNone(deleted_list)  # Should still be deleted
            self.assertIsNotNone(kept_list1)  # Should still exist
            self.assertIsNotNone(kept_list2)  # Should still exist
            
        # Final verification: query all lists and ensure deleted one is not there
        with app.app_context():
            all_lists = TodoList.query.all()
            list_ids = [lst.id for lst in all_lists]
            
            self.assertIn(keep1_id, list_ids)
            self.assertIn(keep2_id, list_ids)
            self.assertNotIn(delete_id, list_ids)


if __name__ == '__main__':
    unittest.main()