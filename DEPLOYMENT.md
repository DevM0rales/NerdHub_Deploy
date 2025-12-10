# Deployment Checklist

## Essential Files for Deployment

1. **Source Code**
   - Nerdhub/ (Django project settings)
   - nucleo/ (Main application)
   - usuarios/ (User management)
   - manage.py (Django management script)

2. **Configuration Files**
   - requirements.txt (Python dependencies)
   - Procfile (Heroku deployment configuration)
   - runtime.txt (Python version specification)

3. **Static and Media Files**
   - nucleo/static/ (CSS, JavaScript, images)
   - media/ (Uploaded files like product images and user avatars)

4. **Database**
   - db.sqlite3 (Application database with data)

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

## Notes

- The application is configured to use SQLite database for development
- Static files are served from nucleo/static/ during development
- For production, static files should be collected to staticfiles/ directory
- The Procfile is configured for Heroku deployment using gunicorn