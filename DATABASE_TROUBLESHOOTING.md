# Database Troubleshooting Guide

This guide helps troubleshoot common database issues with the Pickleball App. If you're encountering database-related errors, follow these steps.

## Common Errors

### 1. "unable to open database file"

This error usually means the application can't access the database file due to:

- The instance directory doesn't exist
- Permissions issues
- Path formatting problems (especially on Windows)

### 2. "No such table" errors

This happens when:

- The database exists but tables haven't been created
- You're connecting to the wrong database
- Database migration issues

### 3. Model relationship errors

These can occur when:

- Circular imports in models
- Duplicate backref definitions
- Improper relationship configurations

## Quick Fixes

### Fix 1: Use the provided batch script

Run `start.bat` (Windows) which handles:

- Virtual environment activation
- Database path configuration
- Database creation and copying if needed

### Fix 2: Check instance directory and permissions

```
# Create the instance directory if it doesn't exist
mkdir -p instance

# Ensure proper permissions (Linux/Mac)
chmod 755 instance
```

### Fix 3: Verify database path in environment variables

Make sure you're using the correct path format for SQLite:

- Use forward slashes even on Windows: `sqlite:///instance/app.db`
- NOT backslashes: `sqlite:///instance\app.db` (will cause errors)

### Fix 4: Recreate the database

If your database is corrupted:

```
# Delete existing database
rm instance/app.db

# Run the application to create a new database
python run.py
```

### Fix 5: Run database initialization manually

```python
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print("Database tables created successfully")
```

Save this as `init_db.py` and run it.

## Advanced Troubleshooting

### Check Database Connection

```python
import sqlite3
conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())
conn.close()
```

Save as `check_db.py` and run it to verify tables exist.

### Debugging Database URL

```python
import os
print(f"Database URL: {os.environ.get('DATABASE_URL', 'Not set')}")
```

### Fixing Model Relationships

If you see "Error creating backref" messages:

1. Check for duplicate backref names across models
2. Ensure relationships aren't defined in both directions with the same backref name
3. Add `overlaps="another_backref_name"` if you need multiple backrefs

## Best Practices

1. Always use the provided scripts (`run.py`, `run_app.py`, or `start.bat`)
2. Don't manually modify the database files
3. Set environment variables correctly
4. Create proper database migrations for schema changes

If issues persist, check the application logs for more specific error messages.
