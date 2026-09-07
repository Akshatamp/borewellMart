# BorewellMart - Borewell Service Marketplace

A professional Borewell Service Marketplace where customers can find, compare, and book verified borewell service providers based on location and required service.

## Technology Stack

- **Backend**: Django (Python)
- **Database**: SQLite3 (Development), PostgreSQL (Production)
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5
- **Authentication**: Django Authentication System
- **Image Storage**: Local Media Storage (Development)

## Features

### Customer Panel
- Browse services without login
- Book services with authentication
- Track bookings
- Give reviews
- Favorite vendors

### Vendor Panel
- Manage services
- Manage gallery
- Accept/reject bookings
- Track earnings
- Profile management

### Admin Panel
- Manage cities, services, vendors
- Verify vendors
- Manage bookings
- View reports and analytics

## Installation

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

5. Run server:
```bash
python manage.py runserver
```

## Project Structure

- `core/` - Main Django app with models, views, templates
- `media/` - Image uploads
- `static/` - CSS, JS, images
- `templates/` - HTML templates
# BorewellMart.Haegl.in
# borewellMart
