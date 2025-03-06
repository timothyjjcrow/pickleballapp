import os
import json
from app import create_app, db
from app.models.user import User

def test_auth():
    """Test authentication endpoints"""
    # Create app with test config
    app = create_app('testing')
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        print("Testing authentication endpoints...")
        
        # Create test client
        client = app.test_client()
        
        # Create test user
        user = User(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        db.session.add(user)
        db.session.commit()
        print(f"Created user: {user}")
        
        # Test login
        print("\nTesting login endpoint...")
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        print(f"Status code: {response.status_code}")
        print(f"Response data: {response.data.decode('utf-8')}")
        
        # Test registration
        print("\nTesting registration endpoint...")
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123'
        })
        print(f"Status code: {response.status_code}")
        print(f"Response data: {response.data.decode('utf-8')}")
        
        # Clean up
        db.session.remove()
        db.drop_all()

if __name__ == "__main__":
    test_auth() 