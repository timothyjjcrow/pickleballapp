# Pickleball App

A web application for scheduling and managing pickleball games. Find courts, schedule games, and connect with other players.

## Features

- User authentication (register, login, profile management)
- Court discovery and search by location
- Game scheduling and management
- Real-time chat for game participants
- Responsive design for mobile and desktop

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: JWT (JSON Web Tokens)

## Getting Started

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Installation

1. Clone the repository

   ```
   git clone https://github.com/your-username/pickleball-app.git
   cd pickleball-app
   ```

2. Create and activate a virtual environment

   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies

   ```
   pip install -r requirements.txt
   ```

4. Initialize and seed the database

   ```
   python scripts/init_db.py     # Create database tables
   python scripts/seed_db.py     # Populate with real court data and sample games
   ```

5. Run the application

   ```
   python run.py
   ```

6. Access the application at http://localhost:5000

## Project Structure

- `app/` - Main application package
  - `api/` - API endpoints
  - `models/` - Database models
  - `services/` - Service layer (search, notifications)
  - `static/` - Static assets (JS, CSS)
  - `templates/` - HTML templates
- `scripts/` - Utility scripts
  - `init_db.py` - Initialize database tables
  - `migrate_courts.py` - Import court data
  - `seed_db.py` - Populate database with sample data
- `instance/` - Instance-specific files
  - `pickleball.db` - SQLite database
- `run.py` - Application entry point
- `wsgi.py` - WSGI entry point for production
- `test_models.py` - Database model tests
- `test_api.py` - API endpoint tests
- `run_tests.py` - Script to run all tests

## Database

The application uses SQLite with SQLAlchemy ORM for data storage.

### Database Models

- **User**: User accounts and authentication
- **Court**: Pickleball court locations with details
- **Game**: Scheduled games with date, time, and skill level
- **GameParticipant**: Many-to-many relationship between games and users
- **ChatMessage**: Messages associated with games

### Database Initialization

The database can be initialized and populated using the provided scripts:

```
python scripts/init_db.py     # Create database tables
python scripts/seed_db.py     # Populate with real court data and sample games
```

The `seed_db.py` script loads real court data from the `courts.json` file located in the root directory. This file contains detailed information about pickleball courts including locations, amenities, hours, and ratings. The script also creates sample users, games, participants, and chat messages to demonstrate the application's functionality.

For more details about the database scripts, see [scripts/README.md](scripts/README.md).

## Testing

The application includes comprehensive tests for database models and API endpoints.

### Running Tests

To run all tests:

```
python run_tests.py
```

To run specific test modules:

```
python test_models.py  # Run model tests only
python test_api.py     # Run API tests only
```

### Test Coverage

- **Model Tests**: Verify database relationships and model functionality
- **API Tests**: Test API endpoints for authentication, courts, games, and user profiles

## Deployment

For production deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
