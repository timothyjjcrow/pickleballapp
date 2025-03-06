# Database Scripts

This directory contains scripts for initializing and seeding the database.

## Available Scripts

### `init_db.py`

Initializes the database by creating all tables defined in the application models.

```bash
python scripts/init_db.py
```

This script:

- Sets necessary environment variables
- Creates a Flask application context
- Creates all database tables using SQLAlchemy's `db.create_all()`

### `migrate_courts.py`

Migrates court data from a JSON file to the database.

```bash
python scripts/migrate_courts.py
```

This script:

- Attempts to load court data from a `courts.json` file
- If the file is not found or cannot be loaded, it creates sample court data
- Clears existing courts from the database
- Creates new court records based on the loaded or sample data
- Attempts to index the courts in Elasticsearch (if available)

### `seed_db.py`

Seeds the database with real court data and sample data for development and testing.

```bash
python scripts/seed_db.py
```

This script:

- Clears existing data from all tables
- Creates sample users with hashed passwords
- Loads real court data from the `courts.json` file in the root directory
  - If the file is not found or cannot be loaded, it creates sample court data
  - The script limits to the first 20 courts for efficiency
- Creates sample games scheduled at different times
- Adds participants to the games
- Adds chat messages for the games

## Database Structure

The database contains the following main tables:

1. `users` - User accounts
2. `courts` - Pickleball court locations
3. `games` - Scheduled games
4. `game_participants` - Many-to-many relationship between games and users
5. `chat_messages` - Messages associated with games

## Development Workflow

For a fresh development setup:

1. Initialize the database:

   ```bash
   python scripts/init_db.py
   ```

2. Seed the database with real court data and sample game data:
   ```bash
   python scripts/seed_db.py
   ```

This will give you a fully functional database with real court data and sample game data for development and testing.

## Court Data

The application uses real court data from the `courts.json` file located in the root directory. This file contains detailed information about pickleball courts including:

- Name and address
- Location coordinates (latitude and longitude)
- Contact information (phone, website)
- Hours of operation
- Court type (indoor, outdoor)
- Surface type
- Amenities
- Ratings and reviews
- Number of courts

The `seed_db.py` script loads this data into the database, making it available for the application to use.
