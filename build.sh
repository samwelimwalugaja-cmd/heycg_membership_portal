#!/bin/bash
set -o errexit

echo "📦 Installing requirements..."
pip install -r requirements.txt

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "📦 Creating media directories..."
mkdir -p media/profile_pics
mkdir -p media/event_images
mkdir -p media/gallery_images
mkdir -p media/blog_images
mkdir -p media/donation_images
mkdir -p media/payment_proofs
mkdir -p media/certificates

echo "📦 Applying migrations..."
python manage.py makemigrations
python manage.py migrate

echo "✅ Build complete!"