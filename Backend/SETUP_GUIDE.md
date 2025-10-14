# Resumify Backend Setup Guide

This guide will walk you through setting up the Resumify backend for development and production.

## 🔧 Quick Setup for Development

### Step 1: Prerequisites

**Required Software:**
- Python 3.8 or higher
- PostgreSQL 12+ (or SQLite for development)
- Git

**Optional (for full features):**
- Redis (for background tasks)
- Node.js (if running frontend alongside)

### Step 2: Environment Setup

```bash
# Clone the repository (if not already done)
cd Backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install spaCy model for NLP
python -m spacy download en_core_web_md
```

### Step 3: Database Configuration

**Option A: PostgreSQL (Recommended)**
```bash
# Install PostgreSQL
# Create database
createdb resumify_db

# Create .env file
cp .env.example .env

# Edit .env file and set:
DATABASE_URL=postgresql://username:password@localhost:5432/resumify_db
```

**Option B: SQLite (Development Only)**
```bash
# Edit .env file and set:
DATABASE_URL=sqlite:///./resumify.db
```

### Step 4: Configuration

Edit the `.env` file with your settings:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/resumify_db

# JWT Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
UPLOAD_FOLDER=./uploads
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=pdf,doc,docx

# CORS (adjust for your frontend URL)
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

### Step 5: Run the Application

```bash
# Start the development server
python main.py

# Alternative using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**✅ Success!** Your API should now be running at:
- Main API: http://localhost:8000
- Interactive Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## 🏗️ Production Setup

### Step 1: Server Requirements

**Recommended Specs:**
- 2+ CPU cores
- 4+ GB RAM
- 50+ GB storage
- Ubuntu 20.04+ or similar

**Required Services:**
- PostgreSQL 12+
- Redis 6+
- Reverse proxy (Nginx recommended)

### Step 2: System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.8 python3.8-venv python3-pip postgresql postgresql-contrib redis-server nginx -y

# Install system packages for PDF processing
sudo apt install poppler-utils tesseract-ocr -y
```

### Step 3: Database Setup

```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database user
sudo -u postgres createuser --createdb --pwprompt resumify_user
# Enter password when prompted

# Create database
sudo -u postgres createdb -O resumify_user resumify_production
```

### Step 4: Application Deployment

```bash
# Create application directory
sudo mkdir -p /var/www/resumify
sudo chown $USER:$USER /var/www/resumify

# Copy application files
cp -r Backend/* /var/www/resumify/
cd /var/www/resumify

# Create virtual environment
python3.8 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server

# Install spaCy model
python -m spacy download en_core_web_md

# Create uploads directory
mkdir -p uploads
chmod 755 uploads
```

### Step 5: Production Configuration

Create `/var/www/resumify/.env`:

```env
# Environment
ENVIRONMENT=production
DEBUG=False

# Database
DATABASE_URL=postgresql://resumify_user:your_password@localhost:5432/resumify_production

# Security
SECRET_KEY=your-very-secure-secret-key-at-least-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
UPLOAD_FOLDER=/var/www/resumify/uploads
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=pdf,doc,docx

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS (adjust for your domain)
BACKEND_CORS_ORIGINS=["https://your-domain.com", "https://www.your-domain.com"]

# Email (optional - for interview notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Step 6: Service Setup

Create systemd service file `/etc/systemd/system/resumify.service`:

```ini
[Unit]
Description=Resumify API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/resumify
Environment=PATH=/var/www/resumify/venv/bin
ExecStart=/var/www/resumify/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Set permissions
sudo chown -R www-data:www-data /var/www/resumify

# Start and enable service
sudo systemctl daemon-reload
sudo systemctl start resumify
sudo systemctl enable resumify

# Check status
sudo systemctl status resumify
```

### Step 7: Nginx Configuration

Create `/etc/nginx/sites-available/resumify`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /uploads/ {
        alias /var/www/resumify/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/resumify /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 8: SSL Certificate (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

## 👤 Initial User Setup

### Create First HR Manager

```bash
# Access the database
sudo -u postgres psql resumify_production

# Create first user (replace with your details)
INSERT INTO users (username, email, full_name, hashed_password, user_type, is_active, created_at)
VALUES (
    'admin',
    'admin@yourcompany.com',
    'HR Administrator',
    '$2b$12$LQv3c1yqBwVHxkd0LHAkCOYz6TtxMQJqhN8/LgRvPKMFjZZpE8/oG',  -- password: admin123
    'hr_manager',
    true,
    NOW()
);

# Exit
\q
```

**⚠️ Important:** Change the default password immediately after first login!

## 🔍 Testing the Installation

### Basic Health Check

```bash
# Test API
curl http://your-domain.com/health

# Expected response:
{"status":"healthy","message":"API is running"}
```

### Test Authentication

```bash
# Login
curl -X POST "http://your-domain.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Should return access token
```

### Test File Upload

```bash
# Test CV upload (replace TOKEN with actual token)
curl -X POST "http://your-domain.com/api/v1/analysis/upload-and-analyze" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@sample_cv.pdf" \
  -F "job_title=Software Developer" \
  -F "job_requirements=Python developer with 2+ years experience"
```

## 📊 Monitoring and Maintenance

### Log Files

```bash
# Application logs
sudo journalctl -u resumify -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database Maintenance

```bash
# Backup database
pg_dump resumify_production > backup_$(date +%Y%m%d_%H%M%S).sql

# Monitor database size
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('resumify_production'));"
```

### Performance Monitoring

```bash
# Monitor application resources
sudo systemctl status resumify
htop

# Monitor database
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity WHERE datname = 'resumify_production';"
```

## ❗ Troubleshooting

### Common Issues

**1. Database Connection Error**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database exists
sudo -u postgres psql -l | grep resumify
```

**2. Permission Errors**
```bash
# Fix file permissions
sudo chown -R www-data:www-data /var/www/resumify
sudo chmod -R 755 /var/www/resumify
sudo chmod -R 777 /var/www/resumify/uploads
```

**3. spaCy Model Missing**
```bash
# Reinstall spaCy model
source /var/www/resumify/venv/bin/activate
python -m spacy download en_core_web_md
```

**4. High Memory Usage**
```bash
# Reduce Gunicorn workers in service file
ExecStart=/var/www/resumify/venv/bin/gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
sudo systemctl daemon-reload
sudo systemctl restart resumify
```

### Performance Optimization

**Database Optimization:**
```sql
-- Add indexes for common queries
CREATE INDEX idx_candidates_name ON candidates(name);
CREATE INDEX idx_cv_analyses_score ON cv_analyses(overall_score);
CREATE INDEX idx_cv_analyses_status ON cv_analyses(match_status);
```

**File Upload Optimization:**
```env
# In .env file
MAX_FILE_SIZE=5242880  # Reduce to 5MB if needed
```

## 🔄 Updates and Deployment

### Update Process

```bash
# Backup first
pg_dump resumify_production > backup_before_update.sql

# Pull updates
cd /var/www/resumify
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart resumify
```

### Zero-Downtime Deployment (Advanced)

1. Set up blue-green deployment
2. Use health checks
3. Implement database migrations
4. Use load balancer for traffic switching

---

## 📞 Support

If you encounter issues:

1. Check the logs: `sudo journalctl -u resumify -f`
2. Verify configuration: review `.env` file
3. Test connectivity: database, Redis, file permissions
4. Review the API documentation at `/docs`

**For development:** Use the development setup above
**For production:** Follow the production setup carefully

The backend is now ready to handle CV parsing, candidate analysis, and interview scheduling for your HR recruitment platform!