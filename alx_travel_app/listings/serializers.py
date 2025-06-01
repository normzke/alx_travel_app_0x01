from rest_framework import serializers
from .models import Listing, Booking, Review
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'created_at']

class BookingSerializer(serializers.ModelSerializer):
    guest = UserSerializer(read_only=True)
    review = ReviewSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'listing', 'guest', 'check_in', 'check_out', 
                 'total_price', 'status', 'created_at', 'review']
        read_only_fields = ['total_price', 'status']

class ListingSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    bookings = BookingSerializer(many=True, read_only=True)

    class Meta:
        model = Listing
        fields = ['id', 'title', 'description', 'address', 'city', 'state',
                 'zipcode', 'price', 'bedrooms', 'bathrooms', 'guests',
                 'property_type', 'owner', 'is_available', 'created_at',
                 'updated_at', 'bookings']
        read_only_fields = ['owner', 'created_at', 'updated_at'] 