from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Listing, Booking, Review
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        
        # Create sample users
        users = []
        for i in range(5):
            user = User.objects.create_user(
                username=f'user{i+1}',
                email=f'user{i+1}@example.com',
                password='password123',
                first_name=f'First{i+1}',
                last_name=f'Last{i+1}'
            )
            users.append(user)
            self.stdout.write(f'Created user: {user.username}')

        # Create sample listings
        property_types = ['HOUSE', 'APARTMENT', 'VILLA', 'CONDO']
        cities = ['New York', 'Los Angeles', 'Chicago', 'Miami', 'Seattle']
        
        listings = []
        for i in range(10):
            listing = Listing.objects.create(
                title=f'Beautiful {property_types[i % 4].lower()} in {cities[i % 5]}',
                description=f'This is a wonderful {property_types[i % 4].lower()} in the heart of {cities[i % 5]}.',
                address=f'{random.randint(1, 999)} Main St',
                city=cities[i % 5],
                state='State',
                zipcode=f'{random.randint(10000, 99999)}',
                price=random.randint(100, 500),
                bedrooms=random.randint(1, 5),
                bathrooms=random.randint(1, 4),
                guests=random.randint(2, 10),
                property_type=property_types[i % 4],
                owner=users[i % 5],
                is_available=True
            )
            listings.append(listing)
            self.stdout.write(f'Created listing: {listing.title}')

        # Create sample bookings
        for i in range(15):
            check_in = datetime.now().date() + timedelta(days=random.randint(1, 30))
            check_out = check_in + timedelta(days=random.randint(1, 7))
            booking = Booking.objects.create(
                listing=random.choice(listings),
                guest=random.choice(users),
                check_in=check_in,
                check_out=check_out,
                total_price=random.randint(100, 1000),
                status=random.choice(['PENDING', 'CONFIRMED', 'COMPLETED'])
            )
            self.stdout.write(f'Created booking: {booking}')

            # Create sample reviews for some bookings
            if booking.status == 'COMPLETED':
                Review.objects.create(
                    booking=booking,
                    rating=random.randint(1, 5),
                    comment=f'Great stay at {booking.listing.title}!'
                )
                self.stdout.write(f'Created review for booking: {booking}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database!')) 