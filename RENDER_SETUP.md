# Render Setup Guide for ASR Parking Lot

## Database Setup

### Option 1: Automatic Setup (Recommended)
The updated `render.yaml` should automatically create a PostgreSQL database. If this doesn't work, follow Option 2.

### Option 2: Manual Database Setup

1. **Go to your Render Dashboard**
   - Visit https://dashboard.render.com
   - Select your ASR Parking Lot project

2. **Add a PostgreSQL Database**
   - Click "New" → "PostgreSQL"
   - Name: `asr-parking-db`
   - Database: `asrparking`
   - User: `asrparking`
   - Region: Choose closest to you
   - Click "Create Database"

3. **Get the Connection String**
   - Click on your new database
   - Go to "Connections" tab
   - Copy the "External Database URL"

4. **Add Environment Variable**
   - Go back to your web service
   - Go to "Environment" tab
   - Add new environment variable:
     - Key: `DATABASE_URL`
     - Value: Paste the connection string you copied

5. **Redeploy**
   - Go to "Manual Deploy" tab
   - Click "Deploy latest commit"

## Default Login Credentials

After successful deployment, you can login with:

### Admin User
- **Email**: admin@asrparking.com
- **Password**: admin123

### Staff User
- **Email**: staff@asrparking.com
- **Password**: staff123

⚠️ **Important**: Change these passwords after first login!

## Troubleshooting

### If you still get database connection errors:

1. **Check the health endpoint**: Visit `your-app-url/health`
2. **Check Render logs**: Go to your web service → "Logs" tab
3. **Verify DATABASE_URL**: Make sure it starts with `postgresql://`
4. **Wait for database**: PostgreSQL databases can take a few minutes to be ready

### Common Issues:

- **Database not ready**: Wait 2-3 minutes after creating the database
- **Wrong connection string**: Make sure to use the External Database URL, not Internal
- **Permission issues**: The database user should have full access to the database

## Testing

1. Visit your app URL
2. Try logging in with the default credentials
3. Check the `/health` endpoint for database status
4. If successful, change the default passwords 