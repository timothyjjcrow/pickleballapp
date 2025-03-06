#!/usr/bin/env python
# Script to create a properly encoded .env file

with open('.env', 'w', encoding='utf-8') as f:
    f.write("""FLASK_APP=app
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your_secret_key
SQLALCHEMY_DATABASE_URI=sqlite:///pickleball.db
ELASTICSEARCH_URL=http://localhost:9200
CORS_ORIGINS=http://localhost:5000
SOCKET_HOST=localhost
SOCKET_PORT=5001
""") 