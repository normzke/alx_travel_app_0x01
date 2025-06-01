# ALX Travel App

A Django-based travel accommodation booking application.

## Project Structure

The project consists of the following main components:

### Models
- `Listing`: Represents available accommodations
- `Booking`: Manages accommodation bookings
- `Review`: Handles user reviews for completed bookings

### API Serializers
- `ListingSerializer`: Handles listing data serialization
- `BookingSerializer`: Manages booking data serialization
- `ReviewSerializer`: Processes review data serialization

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd alx_travel_app
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Seed the database with sample data:
```bash
python manage.py seed
```

## Database Models

### Listing
- Title, description, and location details
- Property specifications (bedrooms, bathrooms, guests)
- Price and availability status
- Owner relationship with User model

### Booking
- Listing and guest relationships
- Check-in and check-out dates
- Total price and booking status
- Created and updated timestamps

### Review
- One-to-one relationship with Booking
- Rating (1-5) and comment
- Timestamps for creation and updates

## API Endpoints

The application provides RESTful API endpoints for:
- Listing management
- Booking operations
- Review submissions

## Development

To run the development server:
```bash
python manage.py runserver
```

## Testing

To run tests:
```bash
python manage.py test
``` 