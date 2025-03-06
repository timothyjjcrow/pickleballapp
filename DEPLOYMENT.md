# Pickleball App Deployment Guide

This document provides instructions on how to deploy the Pickleball App to production.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (venv)
- A web server such as Nginx or Apache for reverse proxy (optional but recommended)

## Local Development vs Production

The application includes configurations for both development and production environments:

- **Development**: Uses Flask's built-in development server with debugging enabled
- **Production**: Uses Waitress WSGI server with debugging disabled and enhanced security

## Deployment Steps

### 1. Clone the Repository

```bash
git clone https://github.com/timothyjjcrow/pickleballapp.git
cd pickleballapp
```

### 2. Set Up a Virtual Environment

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Production Environment Variables

Create a `.env` file in the root directory or set system environment variables:

```
FLASK_ENV=production
FLASK_APP=wsgi.py
SECRET_KEY=your-secure-secret-key
JWT_SECRET_KEY=your-secure-jwt-key
DATABASE_URL=your-database-url
```

For security reasons, use strong, randomly generated keys for `SECRET_KEY` and `JWT_SECRET_KEY`.

### 5. Database Setup

If using a database other than SQLite (recommended for production):

1. Update the `DATABASE_URL` environment variable to point to your production database
2. Run migrations:
   ```bash
   flask db upgrade
   ```

### 6. Run Tests (Recommended)

Before deploying to production, it's recommended to run the test suite to ensure everything is working correctly:

```bash
python run_tests.py
```

Make sure all tests pass before proceeding with the deployment.

### 7. Start the Production Server

#### On Windows

Run the `start_production.bat` script:

```bash
start_production.bat
```

Or directly with Python:

```bash
python -m waitress --port=8000 --host=0.0.0.0 wsgi:app
```

#### On Unix/Linux

Make the start script executable and run it:

```bash
chmod +x start_production.sh
./start_production.sh
```

Or directly with Python:

```bash
python -m waitress --port=8000 --host=0.0.0.0 wsgi:app
```

### 8. Set Up a Reverse Proxy (Recommended)

For production deployments, it's recommended to use a reverse proxy like Nginx or Apache.

#### Nginx Configuration Example

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 9. Set Up SSL (Recommended)

For production, secure your site with HTTPS using Let's Encrypt or another SSL provider.

### 10. Additional Production Considerations

- **Logging**: Configure proper logging to file rather than stdout
- **Monitoring**: Set up application monitoring with tools like Prometheus, Grafana, or a cloud provider's monitoring solution
- **Database Backups**: Implement regular database backups
- **Auto-restart**: Use a process manager like Supervisor, systemd, or PM2 to auto-restart the application if it crashes
- **Continuous Integration**: Set up CI/CD pipelines to run tests automatically before deployment

## Troubleshooting

If you encounter issues with the deployment:

1. Check the application logs
2. Verify that all environment variables are set correctly
3. Ensure the database is accessible and properly configured
4. Check firewall settings to ensure the application port is accessible
5. Run the test suite to identify any issues:
   ```bash
   python run_tests.py
   ```

## Security Considerations

1. Never expose the development server to the internet
2. Always use strong, unique keys for `SECRET_KEY` and `JWT_SECRET_KEY`
3. Consider implementing rate limiting
4. Keep all packages updated to patch security vulnerabilities
5. Regularly audit your application for security issues
6. Run security-focused tests regularly
