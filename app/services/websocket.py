import asyncio
import json
import logging
import websockets
from datetime import datetime

logger = logging.getLogger(__name__)

# Store active connections
connections = {}

async def register(websocket, game_id, user_id):
    """Register a new WebSocket connection for a game"""
    if game_id not in connections:
        connections[game_id] = {}
    
    connections[game_id][user_id] = websocket
    logger.info(f"User {user_id} connected to game {game_id}")
    
    # Notify other users in the game
    await notify_users(game_id, {
        'type': 'user_joined',
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat()
    })

async def unregister(game_id, user_id):
    """Unregister a WebSocket connection"""
    if game_id in connections and user_id in connections[game_id]:
        del connections[game_id][user_id]
        logger.info(f"User {user_id} disconnected from game {game_id}")
        
        # Notify other users in the game
        await notify_users(game_id, {
            'type': 'user_left',
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Clean up empty games
        if not connections[game_id]:
            del connections[game_id]

async def notify_users(game_id, message):
    """Send a message to all users in a game"""
    if game_id in connections:
        disconnected_users = []
        
        for user_id, websocket in connections[game_id].items():
            try:
                await websocket.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            await unregister(game_id, user_id)

async def chat_server(websocket, path):
    """WebSocket server for chat"""
    try:
        # Authenticate the connection (in a real app, verify JWT)
        auth_message = await websocket.recv()
        auth_data = json.loads(auth_message)
        
        if 'game_id' not in auth_data or 'user_id' not in auth_data or 'token' not in auth_data:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Authentication failed: Missing required fields'
            }))
            return
        
        game_id = auth_data['game_id']
        user_id = auth_data['user_id']
        token = auth_data['token']
        
        # TODO: Verify token with JWT
        # For now, we'll just accept any token
        
        # Register the connection
        await register(websocket, game_id, user_id)
        
        # Send confirmation
        await websocket.send(json.dumps({
            'type': 'connected',
            'game_id': game_id,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }))
        
        # Handle messages
        async for message in websocket:
            try:
                data = json.loads(message)
                
                if 'type' not in data:
                    continue
                
                if data['type'] == 'chat':
                    # Broadcast chat message to all users in the game
                    await notify_users(game_id, {
                        'type': 'chat',
                        'user_id': user_id,
                        'message': data.get('message', ''),
                        'timestamp': datetime.utcnow().isoformat()
                    })
                elif data['type'] == 'typing':
                    # Notify that user is typing
                    await notify_users(game_id, {
                        'type': 'typing',
                        'user_id': user_id,
                        'timestamp': datetime.utcnow().isoformat()
                    })
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from user {user_id}")
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Connection closed")
    finally:
        # Unregister on disconnect
        if 'game_id' in locals() and 'user_id' in locals():
            await unregister(game_id, user_id)

def start_websocket_server(host='localhost', port=8765):
    """Start the WebSocket server"""
    logger.info(f"Starting WebSocket server on {host}:{port}")
    return websockets.serve(chat_server, host, port)

# Example of how to run the server
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(start_websocket_server())
#     loop.run_forever() 