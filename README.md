# ALX Travel App API

This is the API for the ALX Travel App, providing endpoints for managing listings and bookings.

## Setup

1. Clone the repository
2. Create a virtual environment and activate it
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your environment variables in a `.env` file:
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
   SQL_ENGINE=django.db.backends.mysql
   SQL_DATABASE=your_database_name
   SQL_USER=your_database_user
   SQL_PASSWORD=your_database_password
   SQL_HOST=localhost
   SQL_PORT=3306
   ```
5. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## API Documentation

The API documentation is available at:
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`

## API Endpoints

### Listings

- `GET /api/listings/` - List all listings
- `POST /api/listings/` - Create a new listing
- `GET /api/listings/{id}/` - Retrieve a specific listing
- `PUT /api/listings/{id}/` - Update a listing
- `DELETE /api/listings/{id}/` - Delete a listing
- `GET /api/listings/{id}/bookings/` - Get all bookings for a listing

### Bookings

- `GET /api/bookings/` - List all bookings (filtered by user)
- `POST /api/bookings/` - Create a new booking
- `GET /api/bookings/{id}/` - Retrieve a specific booking
- `PUT /api/bookings/{id}/` - Update a booking
- `DELETE /api/bookings/{id}/` - Delete a booking
- `POST /api/bookings/{id}/confirm/` - Confirm a booking
- `POST /api/bookings/{id}/cancel/` - Cancel a booking

## Authentication

The API uses Django's built-in authentication system. Most endpoints require authentication, except for listing retrieval which is publicly accessible.

## Testing

You can test the API endpoints using tools like Postman or curl. Make sure to include the appropriate authentication headers when making requests to protected endpoints. 