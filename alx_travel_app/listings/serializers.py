from rest_framework import serializers
from .models import Listing, Booking
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ListingSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Listing
        fields = ['id', 'title', 'description', 'price', 'location', 
                 'created_at', 'updated_at', 'owner']
        read_only_fields = ['created_at', 'updated_at']

class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(),
        write_only=True,
        source='listing'
    )

    class Meta:
        model = Booking
        fields = ['id', 'listing', 'listing_id', 'user', 'check_in', 
                 'check_out', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at'] 