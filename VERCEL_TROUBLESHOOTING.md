# Vercel Deployment Troubleshooting Guide

This guide provides solutions for common issues you might encounter when deploying your Flask application to Vercel.

## Common Error: 500 INTERNAL_SERVER_ERROR

If you see an error like:

```
500: INTERNAL_SERVER_ERROR
Code: FUNCTION_INVOCATION_FAILED
ID: pdx1::8zjm6-1741227169885-0e9578c59f8f
```

### Potential Causes and Solutions

#### 1. Database Connection Issues

**Problem**: SQLite doesn't work well in Vercel's serverless environment due to its ephemeral filesystem.

**Solution**:

- Use a hosted PostgreSQL database (recommended for production)
- Set the `DATABASE_URL` environment variable in Vercel project settings
- Example PostgreSQL URL: `postgresql://username:password@host:port/database`
- Free options:
  - [Neon](https://neon.tech)
  - [ElephantSQL](https://www.elephantsql.com)
  - [Supabase](https://supabase.com)

#### 2. Missing Environment Variables

**Problem**: Required environment variables not set in Vercel.

**Solution**:

- Set these environment variables in your Vercel project settings:
  - `SECRET_KEY`
  - `JWT_SECRET_KEY`
  - `DATABASE_URL`

#### 3. File System Access

**Problem**: Trying to read/write files in locations that don't exist in Vercel.

**Solution**:

- Only `/tmp` directory is writable in Vercel functions
- Do not rely on the filesystem for persistent storage in Vercel

#### 4. Function Timeout

**Problem**: Your function execution takes too long.

**Solution**:

- Check the `vercel.json` file's `functions` section for timeout settings
- Optimize database queries and code execution
- Consider serverless-friendly architecture

## Debugging Your Deployment

### 1. Visit the Debug Endpoint

Go to your deployed app's `/debug` endpoint to see detailed diagnostic information:

```
https://your-project.vercel.app/debug
```

### 2. Check Vercel Logs

- Go to the Vercel dashboard
- Select your project
- Click on the latest deployment
- Go to "Functions" tab
- Click on the function that's failing
- Check the logs for error messages

### 3. Local Testing

Test your app with environmental variables similar to Vercel:

```bash
VERCEL=1 FLASK_ENV=production DATABASE_URL=your_database_url python debug.py
```

## Database Recommendations for Production

For a production deployment on Vercel, we strongly recommend using a hosted PostgreSQL database rather than SQLite. This ensures data persistence between function invocations and provides better scalability.

Free PostgreSQL hosting options:

- [Neon](https://neon.tech) - Modern serverless Postgres
- [ElephantSQL](https://www.elephantsql.com) - PostgreSQL as a Service
- [Supabase](https://supabase.com) - Open source Firebase alternative with PostgreSQL

## Contact Support

If you continue to have issues after trying these solutions, please:

1. Collect detailed error logs from Vercel
2. Gather the output from the `/debug` endpoint
3. Contact support with this information
