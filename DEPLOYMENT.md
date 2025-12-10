# Deployment Checklist

## Essential Files for Deployment

1. **Source Code**
   - Nerdhub/ (Django project settings)
   - nucleo/ (Main application)
   - usuarios/ (User management)
   - manage.py (Django management script)

2. **Configuration Files**
   - requirements.txt (Python dependencies)
   - Procfile (Heroku/Railway deployment configuration)
   - runtime.txt (Python version specification)

3. **Static and Media Files**
   - nucleo/static/ (CSS, JavaScript, images)
   - media/ (Uploaded files like product images and user avatars)

4. **Database**
   - db.sqlite3 (Application database with data - for development only)

## Deployment Steps

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Collect static files (for production):
   ```
   python manage.py collectstatic
   ```

3. Run migrations (if needed):
   ```
   python manage.py migrate
   ```

4. Start the server:
   ```
   gunicorn Nerdhub.wsgi
   ```

## Railway-Specific Configuration

1. **Environment Variables**:
   - `DJANGO_SECRET_KEY` - Generate a secure random string (required)
   - `DEBUG` - Set to `False` (required for production)
   - `DJANGO_ALLOWED_HOSTS` - Include your Railway domain (e.g., `your-app.up.railway.app`)
   - `DATABASE_URL` - Provided automatically by Railway (no need to set manually)

2. **Database**:
   - Railway automatically provides a PostgreSQL database
   - The application is configured to use PostgreSQL when `DATABASE_URL` is present
   - For local development, SQLite is still used

## Notes

- The application automatically detects Railway deployment through the `DATABASE_URL` environment variable
- Static files are served using WhiteNoise for production
- For local development, static files are served from nucleo/static/
- For production, static files should be collected to staticfiles/ directory
- The Procfile is configured for Heroku/Railway deployment using gunicorn