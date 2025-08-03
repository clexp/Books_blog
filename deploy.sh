#!/bin/bash

# Django Book Blog Production Deployment Script
# For FreeBSD VM with Apache

set -e  # Exit on any error

echo "🚀 Starting Django Book Blog deployment..."

# Update from git
echo "📥 Pulling latest changes from git..."
git pull origin main

# Activate virtual environment (adjust path as needed)
echo "🐍 Activating Python virtual environment..."
source venv/bin/activate

# Install/update production requirements
echo "📦 Installing production requirements..."
pip install -r requirements_production.txt

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Set proper permissions
echo "🔐 Setting file permissions..."
chmod 755 staticfiles/
chmod 755 media/

# Restart Apache (adjust service name as needed)
echo "🔄 Restarting Apache..."
sudo service apache24 restart

# Test the application
echo "🧪 Testing application..."
python manage.py check --deploy

echo "✅ Deployment completed successfully!"
echo "🌐 Your site should be available at: https://books.clexp.net" 