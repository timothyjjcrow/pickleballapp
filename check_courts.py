import sqlite3
import json

# Connect to the database
conn = sqlite3.connect('instance/pickleball.db')
conn.row_factory = sqlite3.Row  # This enables column access by name
cursor = conn.cursor()

# Get the first 3 courts to verify
cursor.execute('SELECT * FROM courts LIMIT 3')
courts = cursor.fetchall()

# Print court details
for i, court in enumerate(courts, 1):
    print(f"Court {i}:")
    print(f"  Name: {court['name']}")
    print(f"  Address: {court['address']}")
    print(f"  Rating: {court['rating']}")
    print(f"  Number of Courts: {court['number_of_courts']}")
    
    # Parse and print amenities if they exist
    if court['amenities']:
        try:
            amenities = json.loads(court['amenities'])
            print(f"  Amenities: {', '.join(amenities) if isinstance(amenities, list) else amenities}")
        except json.JSONDecodeError:
            print(f"  Amenities: {court['amenities']} (not in JSON format)")
    
    print("")

# Close the connection
conn.close() 