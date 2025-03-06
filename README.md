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
- **Database**: SQLite with SQLAlchemy ORM (local/dev) / PostgreSQL (production)
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

4. Initialize the database

   ```
   python manage.py setup-db
   ```

5. Run the application

   ```
   python manage.py run
   ```

6. Access the application at http://localhost:8000

## Using the Management Script

The `manage.py` script provides a unified command-line interface for common tasks:

```
python manage.py [command] [options]
```

Available commands:

- **run**: Start the Flask application

  ```
  python manage.py run [--env development|production|testing] [--debug] [--port PORT]
  ```

- **setup-db**: Initialize the database

  ```
  python manage.py setup-db [--env development|production|testing]
  ```

- **migrate**: Run database migrations

  ```
  python manage.py migrate [--env development|production|testing]
  ```

- **test**: Run the test suite

  ```
  python manage.py test [--test-path PATH]
  ```

- **create-env**: Create or update .env file
  ```
  python manage.py create-env [--env development|production|testing] [--db-url URL] [--force]
  ```

## Project Structure

- `app/` - Main application package
  - `api/` - API endpoints
  - `models/` - Database models
  - `services/` - Service layer (search, notifications)
  - `static/` - Static assets (JS, CSS)
  - `templates/` - HTML templates
- `scripts/` - Utility scripts
- `migrations/` - Database migration scripts
- `instance/` - Instance-specific files
  - `pickleball.db` - SQLite database (development)
- `manage.py` - Management script for common tasks
- `run.py` - Application entry point
- `wsgi.py` - WSGI entry point for production
- `config.py` - Application configuration
- `init_db.py` - Database initialization
- `test_*.py` - Test files

## Database

The application uses SQLite with SQLAlchemy ORM for local development and testing, and PostgreSQL for production.

### Database Models

- **User**: User accounts and authentication
- **Court**: Pickleball court locations with details
- **Game**: Scheduled games with date, time, and skill level
- **GameParticipant**: Many-to-many relationship between games and users
- **ChatMessage**: Messages associated with games

### Database Initialization and Migration

The database can be initialized and migrated using the management script:

```
# Initialize database for development
python manage.py setup-db --env development

# Run migrations for production
python manage.py migrate --env production
```

## Testing

The application includes comprehensive tests for database models and API endpoints.

### Running Tests

To run all tests:

```
python manage.py test
```

To run specific test files:

```
python manage.py test --test-path test_models.py
```

### Test Coverage

- **Model Tests**: Verify database relationships and model functionality
- **API Tests**: Test API endpoints for authentication, courts, games, and user profiles

## Deployment

For production deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Deployment Options

### Local Development

See the [local setup instructions](#setup-and-installation).

### Vercel Deployment

For deploying to Vercel, see [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md).

### Heroku Deployment

For deploying to Heroku, see [HEROKU_DEPLOYMENT.md](HEROKU_DEPLOYMENT.md).

Heroku deployment uses PostgreSQL for the database, ensuring data persistence across application restarts and deployments.

#### Quick Heroku Deployment Steps:

1. Create a Heroku account and install the Heroku CLI
2. Create a new Heroku app: `heroku create`
3. Add PostgreSQL: `heroku addons:create heroku-postgresql:mini`
4. Deploy your code: `git push heroku main`
5. Open the app: `heroku open`

For detailed instructions, see [HEROKU_DEPLOYMENT.md](HEROKU_DEPLOYMENT.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
