# Deploying to Heroku

This guide will walk you through the process of deploying the Pickleball App to Heroku.

## Prerequisites

1. A [Heroku account](https://signup.heroku.com/)
2. [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed on your machine
3. Git installed on your machine

## Setup

### 1. Login to Heroku CLI

```bash
heroku login
```

### 2. Create a Heroku app

```bash
heroku create pickleball-app
```

Or if you want Heroku to generate a name for you:

```bash
heroku create
```

### 3. Add PostgreSQL add-on

```bash
heroku addons:create heroku-postgresql:mini
```

This adds the PostgreSQL add-on with the "mini" plan (free tier has been discontinued, this is the lowest cost option).

### 4. Set environment variables

Set the necessary environment variables for the application:

```bash
heroku config:set FLASK_APP=app
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key
heroku config:set JWT_SECRET_KEY=your-jwt-secret-key
```

Replace `your-secret-key` and `your-jwt-secret-key` with secure random strings.

### 5. Initialize the Git repository (if not already initialized)

```bash
git init
git add .
git commit -m "Initial commit for Heroku deployment"
```

### 6. Deploy to Heroku

```bash
git push heroku main
```

Or if you're on a branch named `master`:

```bash
git push heroku master
```

### 7. Run database migrations

This step should happen automatically as part of the release phase defined in the Procfile. However, if you need to run it manually:

```bash
heroku run python migrations/create_or_migrate_db.py
```

### 8. Open your app

```bash
heroku open
```

## Additional Configuration

### Scaling dynos

By default, Heroku will run your app on 1 web dyno. To scale up or down:

```bash
heroku ps:scale web=1
```

### View logs

To see the application logs:

```bash
heroku logs --tail
```

### Database management

To access the PostgreSQL database directly:

```bash
heroku pg:psql
```

## Troubleshooting

### Application Error

If you see an "Application Error" when opening the app, check the logs:

```bash
heroku logs --tail
```

### Database Issues

If you're experiencing database-related issues:

1. Check if the DATABASE_URL environment variable is correctly set:

```bash
heroku config:get DATABASE_URL
```

2. Try running the database creation script manually:

```bash
heroku run python migrations/create_or_migrate_db.py
```

3. Check if the database tables are created:

```bash
heroku pg:psql
```

Then in the PostgreSQL shell:

```sql
\dt
```

### Deployment Issues

If you're having problems deploying:

1. Make sure all your changes are committed:

```bash
git status
```

2. Check that your Heroku remote is set up correctly:

```bash
git remote -v
```

3. If not, add it:

```bash
heroku git:remote -a your-app-name
```

## Important Notes

1. Heroku uses an ephemeral filesystem, meaning any files written to the filesystem will be lost when the dyno restarts.
   Do not rely on the filesystem for persistent storage.

2. Heroku automatically sets the `PORT` environment variable, which your app should use for the web server.

3. Use PostgreSQL for your database as SQLite won't work well in Heroku's ephemeral filesystem.

4. Free tier dynos will "sleep" after 30 minutes of inactivity, causing a delay on the first request after inactivity.
