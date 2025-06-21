# Deployment Guide - Persistent Database Setup

## Problem Solved
Your application was losing data because it was using SQLite with local file storage, which gets reset when Render restarts your service.

## Solution: PostgreSQL Database
We've migrated your application to use PostgreSQL, which provides persistent storage on Render.

## Changes Made

### 1. Database Configuration (`app/__init__.py`)
- Modified to use PostgreSQL when `DATABASE_URL` environment variable is available
- Falls back to SQLite for local development

### 2. Dependencies (`requirements.txt`)
- Added `psycopg2-binary==2.9.7` for PostgreSQL support

### 3. Render Configuration (`render.yaml`)
- Added PostgreSQL database service
- Linked database to web service
- Updated build command to run database migrations

### 4. Database Migration (`migrate_db.py`)
- Created script to handle database setup and migrations
- Automatically creates default users if they don't exist

## Deployment Steps

### 1. Push Changes to GitHub
```bash
git add .
git commit -m "Add PostgreSQL support for persistent data storage"
git push origin main
```

### 2. Deploy on Render
1. Go to your Render dashboard
2. Your service will automatically redeploy with the new configuration
3. Render will create a new PostgreSQL database
4. The build process will run migrations and create default users

### 3. Verify Deployment
- Check that your application is running
- Log in with default credentials:
  - Admin: `admin` / `azeedmr123`
  - Staff: `staff` / `staff1@54321`
- Add some test vehicle entries
- Restart your service to verify data persistence

## Local Development

For local development, create a `.env` file:
```
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=your-secret-key-here
```

The application will automatically use SQLite for local development.

## Database Management

### View Database on Render
1. Go to your Render dashboard
2. Click on the "asr-parking-db" database
3. Use the "Connect" button to access the database

### Backup Data
Render automatically backs up PostgreSQL databases. You can also:
1. Use the database connection string from Render dashboard
2. Connect with a PostgreSQL client
3. Export your data

## Troubleshooting

### If migrations fail:
1. Check the build logs in Render
2. Ensure all dependencies are installed
3. Verify the database connection string

### If data still resets:
1. Verify the `DATABASE_URL` environment variable is set
2. Check that the database service is running
3. Ensure migrations completed successfully

## Benefits of This Solution

1. **Persistent Data**: Your vehicle entries will survive service restarts
2. **Automatic Backups**: Render provides automatic database backups
3. **Scalability**: PostgreSQL can handle more data and concurrent users
4. **Reliability**: Database is managed by Render, reducing maintenance overhead 