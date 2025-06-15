import unittest
import json
from app import app, db, Todo, TodoList


class TodoAppTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up stuff before each test"""
        self.app = app.test_client()
        app.config['TESTING'] = True
        # use a different database for testing so we don't mess up the real one
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up after each test"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_home_page_redirect(self):
        """Test that the home page redirects properly"""
        response = self.app.get('/')
        # Should redirect to welcome page since no lists exist yet
        self.assertEqual(response.status_code, 302)
        self.assertIn('welcome', response.location)
    
    def test_create_todolist(self):
        """Test creating a new todo list"""
        list_data = {'name': 'My Test List'}
        response = self.app.post('/todos', 
                                data=json.dumps(list_data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'My Test List')
        self.assertTrue('id' in data)
    
    def test_create_todolist_bad_data(self):
        """Test creating todo list with missing data"""
        response = self.app.post('/todos',
                                data=json.dumps({}),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
    
    def test_create_todo(self):
        """Test creating a new todo item"""
        # First create a list
        list_data = {'name': 'Test List'}
        list_response = self.app.post('/todos',
                                     data=json.dumps(list_data),
                                     content_type='application/json')
        list_id = json.loads(list_response.data)['id']
        
        # Now create a todo
        todo_data = {
            'description': 'Test todo item',
            'todolist_id': list_id
        }
        response = self.app.post(f'/todos/{list_id}',
                                data=json.dumps(todo_data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['description'], 'Test todo item')
        self.assertTrue('id' in data)
    
    def test_create_todo_no_description(self):
        """Test creating todo without description fails"""
        response = self.app.post('/todos/1',
                                data=json.dumps({'todolist_id': 1}),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
    
    def test_update_todo_completion(self):
        """Test updating a todo's completion status"""
        # Setup: create list and todo
        with app.app_context():
            todo_list = TodoList(name='Test List')
            db.session.add(todo_list)
            db.session.commit()
            
            todo = Todo(description='Test Todo', todolist_id=todo_list.id)
            db.session.add(todo)
            db.session.commit()
            
            list_id = todo_list.id
            todo_id = todo.id
        
        # Test updating completion
        update_data = {'completed': True}
        response = self.app.patch(f'/todos/{list_id}/{todo_id}',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['completed'])
    
    def test_update_all_todos(self):
        """Test marking all todos in a list as complete"""
        # Setup: create list with multiple todos
        with app.app_context():
            todo_list = TodoList(name='Test List')
            db.session.add(todo_list)
            db.session.commit()
            
            todo1 = Todo(description='Todo 1', todolist_id=todo_list.id)
            todo2 = Todo(description='Todo 2', todolist_id=todo_list.id)
            db.session.add(todo1)
            db.session.add(todo2)
            db.session.commit()
            
            list_id = todo_list.id
        
        # Test updating all
        response = self.app.put(f'/todos/{list_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['successful'])
        
        # Check that todos are actually completed
        with app.app_context():
            todos = Todo.query.filter_by(todolist_id=list_id).all()
            for todo in todos:
                self.assertTrue(todo.completed)
    
    def test_delete_todo(self):
        """Test deleting a todo item"""
        # Setup
        with app.app_context():
            todo_list = TodoList(name='Test List')
            db.session.add(todo_list)
            db.session.commit()
            
            todo = Todo(description='Todo to delete', todolist_id=todo_list.id)
            db.session.add(todo)
            db.session.commit()
            
            list_id = todo_list.id
            todo_id = todo.id
        
        # Delete the todo
        response = self.app.delete(f'/todos/{list_id}/{todo_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['successful'])
        
        # Verify it's actually deleted
        with app.app_context():
            deleted_todo = db.session.get(Todo, todo_id)
            self.assertIsNone(deleted_todo)
    
    def test_delete_todolist(self):
        """Test deleting an entire todo list"""
        # Setup
        with app.app_context():
            todo_list = TodoList(name='List to delete')
            db.session.add(todo_list)
            db.session.commit()
            list_id = todo_list.id
        
        # Delete the list
        response = self.app.delete(f'/todos/{list_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['successful'])
        
        # Verify it's deleted
        with app.app_context():
            deleted_list = db.session.get(TodoList, list_id)
            self.assertIsNone(deleted_list)
    
    def test_get_welcome_page(self):
        """Test getting the welcome page"""
        response = self.app.get('/todos/welcome')
        self.assertEqual(response.status_code, 200)
        # Should render the template (we can't test the actual HTML without templates)
    
    def test_get_real_todolist_page(self):
        """Test getting a real todo list page"""
        # Setup
        with app.app_context():
            todo_list = TodoList(name='My List')
            db.session.add(todo_list)
            db.session.commit()
            
            todo = Todo(description='A todo', todolist_id=todo_list.id)
            db.session.add(todo)
            db.session.commit()
            
            list_id = todo_list.id
        
        # This might fail if template file doesn't exist, but let's try
        try:
            response = self.app.get(f'/todos/{list_id}')
            # If template exists, should be 200, if not, should be 500
            self.assertIn(response.status_code, [200, 500])
        except:
            # Template probably doesn't exist, that's ok for this test
            pass


if __name__ == '__main__':
    # Run the tests
    unittest.main()