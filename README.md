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

4. Run the application

   ```
   python run.py
   ```

5. Access the application at http://localhost:5000

## Project Structure

- `app/` - Main application package
  - `api/` - API endpoints
  - `models/` - Database models
  - `services/` - Service layer (search, notifications)
  - `static/` - Static assets (JS, CSS)
  - `templates/` - HTML templates
- `run.py` - Application entry point

## License

This project is licensed under the MIT License - see the LICENSE file for details.
