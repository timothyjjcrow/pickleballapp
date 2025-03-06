# Deploying to Vercel

This guide provides instructions for deploying the Pickleball App to Vercel.

## Prerequisites

- A Vercel account (sign up at https://vercel.com)
- Git repository with your project
- The Vercel CLI (optional, for local testing)

## Configuration Files

The project includes the following configuration files for Vercel deployment:

- `vercel.json`: Configures build settings and routes
- `runtime.txt`: Specifies the Python version
- `.vercelignore`: Excludes files from deployment

## Environment Variables

You'll need to set the following environment variables in your Vercel project:

1. `SECRET_KEY`: A secure secret key for Flask
2. `JWT_SECRET_KEY`: A secure key for JWT tokens
3. `DATABASE_URL`: Your database connection string

For a production deployment, you should use a hosted database (e.g., PostgreSQL on Supabase, Neon, or Railway) instead of SQLite.

## Deployment Steps

### Using the Vercel Dashboard

1. Push your project to a Git repository (GitHub, GitLab, or Bitbucket)
2. Log in to your Vercel account
3. Click "New Project"
4. Import your Git repository
5. Configure the project:
   - Set the appropriate framework preset (Python)
   - Configure environment variables
   - Set the build command and output directory if needed
6. Click "Deploy"

### Using the Vercel CLI

1. Install the Vercel CLI:

   ```
   npm install -g vercel
   ```

2. Log in to your Vercel account:

   ```
   vercel login
   ```

3. Deploy the project:

   ```
   vercel
   ```

4. Follow the interactive prompts to configure and deploy your project

## Database Considerations

Vercel uses a serverless architecture, which has implications for database connections:

- **SQLite**: Works but is not recommended for production as the filesystem is ephemeral

  - Data will be stored in `/tmp` and may be reset between function invocations
  - Good for demos or testing only

- **Hosted Databases**: Use a hosted database service for production
  - Update the `DATABASE_URL` environment variable in Vercel
  - Ensure the database allows connections from Vercel's IP ranges

## Troubleshooting

If you encounter issues with your Vercel deployment:

1. Check the Vercel deployment logs for error messages
2. Verify that all required environment variables are set
3. Ensure that the database connection is working
4. Test with the Vercel CLI using `vercel dev` for local testing

## Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/functions/runtimes/python)
- [Vercel Environment Variables](https://vercel.com/docs/projects/environment-variables)
