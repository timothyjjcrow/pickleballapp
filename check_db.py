import sqlite3

# Connect to the database
conn = sqlite3.connect('instance/pickleball.db')
cursor = conn.cursor()

# Check courts table
cursor.execute('SELECT COUNT(*) FROM courts')
court_count = cursor.fetchone()[0]
print(f'Number of courts: {court_count}')

# Check users table
cursor.execute('SELECT COUNT(*) FROM users')
user_count = cursor.fetchone()[0]
print(f'Number of users: {user_count}')

# Check games table
cursor.execute('SELECT COUNT(*) FROM games')
game_count = cursor.fetchone()[0]
print(f'Number of games: {game_count}')

# Check game_participants table
cursor.execute('SELECT COUNT(*) FROM game_participants')
participant_count = cursor.fetchone()[0]
print(f'Number of participants: {participant_count}')

# Check chat_messages table
cursor.execute('SELECT COUNT(*) FROM chat_messages')
message_count = cursor.fetchone()[0]
print(f'Number of chat messages: {message_count}')

# Close the connection
conn.close() 