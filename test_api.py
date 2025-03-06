import os
import json
import unittest
from datetime import datetime, time, date, timedelta
from app import create_app, db
from app.models.user import User
from app.models.court import Court
from app.models.game import Game, GameParticipant
from app.models.chat import ChatMessage

class TestAPI(unittest.TestCase):
    """Test case for the API endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
        # Create test user
        self.user = User(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        db.session.add(self.user)
        
        # Create another test user
        self.user2 = User(
            username='testuser2',
            email='test2@example.com',
            password='password123'
        )
        db.session.add(self.user2)
        
        # Create test court
        self.court = Court(
            uuid='test-court-123',
            name='Test Court',
            address='123 Test Ave, Testville',
            lat=40.7128,
            lng=-74.0060
        )
        db.session.add(self.court)
        
        # Create test game
        tomorrow = date.today() + timedelta(days=1)
        self.game = Game(
            court_id=1,  # Will be set after commit
            creator_id=1,  # Will be set after commit
            date=tomorrow,
            time=time(14, 0),  # 2:00 PM
            max_players=4,
            skill_level='intermediate',
            notes='Test game'
        )
        
        db.session.commit()
        
        # Update game with correct IDs
        self.game.court_id = self.court.court_id
        self.game.creator_id = self.user.user_id
        db.session.add(self.game)
        db.session.commit()
        
        # Add creator as participant
        self.participant = GameParticipant(
            game_id=self.game.game_id,
            user_id=self.user.user_id
        )
        db.session.add(self.participant)
        db.session.commit()
        
        # Get auth token for test user
        response = self.client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        data = json.loads(response.data)
        self.token = data.get('access_token')
    
    def tearDown(self):
        """Tear down test environment"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\nTesting auth endpoints...")
        
        # Test registration
        response = self.client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        print("✓ Registration endpoint works")
        
        # Test login
        response = self.client.post('/api/auth/login', json={
            'username': 'newuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        print("✓ Login endpoint works")
    
    def test_court_endpoints(self):
        """Test court endpoints"""
        print("\nTesting court endpoints...")
        
        # Test get all courts
        response = self.client.get('/api/courts')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('courts', data)
        self.assertIsInstance(data['courts'], list)
        self.assertEqual(len(data['courts']), 1)
        print("✓ Get all courts endpoint works")
        
        # Test get court by ID
        response = self.client.get(f'/api/courts/{self.court.court_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Test Court')
        print("✓ Get court by ID endpoint works")
    
    def test_game_endpoints(self):
        """Test game endpoints"""
        print("\nTesting game endpoints...")
        
        # Test get all games
        response = self.client.get('/api/games')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('games', data)
        self.assertIsInstance(data['games'], list)
        self.assertEqual(len(data['games']), 1)
        print("✓ Get all games endpoint works")
        
        # Test get game by ID
        response = self.client.get(f'/api/games/{self.game.game_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('game', data)
        self.assertEqual(data['game']['notes'], 'Test game')
        print("✓ Get game by ID endpoint works")
        
        # Test create game (requires auth)
        tomorrow = date.today() + timedelta(days=1)
        game_time = time(16, 0)  # 4:00 PM
        
        response = self.client.post(
            '/api/games',
            json={
                'court_id': self.court.court_id,
                'date': tomorrow.isoformat(),
                'time': game_time.strftime('%H:%M'),  # Format as HH:MM
                'max_players': 4,
                'skill_level': 'beginner',
                'notes': 'New test game'
            },
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Print response for debugging
        print(f"Create game response: {response.status_code}")
        print(f"Response data: {response.data.decode('utf-8')}")
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('game', data)
        self.assertEqual(data['game']['notes'], 'New test game')
        print("✓ Create game endpoint works")
        
        # Test join game (requires auth)
        new_game_id = data['game_id']
        
        # Get the game to check participants
        response = self.client.get(f'/api/games/{new_game_id}')
        self.assertEqual(response.status_code, 200)
        game_data = json.loads(response.data)
        print(f"Game before joining: {json.dumps(game_data, indent=2)}")
        
        # Try to join the game
        response = self.client.post(
            f'/api/games/{new_game_id}/join',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Print response for debugging
        print(f"Join game response: {response.status_code}")
        print(f"Response data: {response.data.decode('utf-8')}")
        
        # We expect a 400 because the user is already a participant (creator)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'You are already a participant in this game')
        print("✓ Join game validation works")
        
        # Test with a different user
        # Get token for second user
        response = self.client.post('/api/auth/login', json={
            'username': 'testuser2',
            'password': 'password123'
        })
        data = json.loads(response.data)
        token2 = data.get('access_token')
        
        # Join with second user
        response = self.client.post(
            f'/api/games/{new_game_id}/join',
            headers={'Authorization': f'Bearer {token2}'}
        )
        
        # Print response for debugging
        print(f"Join game (user2) response: {response.status_code}")
        print(f"Response data: {response.data.decode('utf-8')}")
        
        self.assertEqual(response.status_code, 200)
        print("✓ Join game endpoint works with different user")
    
    def test_user_profile(self):
        """Test user profile endpoint"""
        print("\nTesting user profile endpoint...")
        
        # Test get user profile (requires auth)
        response = self.client.get(
            '/api/auth/profile',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['username'], 'testuser')
        print("✓ Get user profile endpoint works")

if __name__ == '__main__':
    unittest.main() 