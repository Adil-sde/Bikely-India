from rest_framework import serializers
from .models import Bike, InspectionReport, Booking, BikeImage

class BikeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeImage
        fields = ['id', 'image', 'caption']

class InspectionReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionReport
        fields = '__all__'

class BikeCatalogSerializer(serializers.ModelSerializer):
    inspection = InspectionReportSerializer(read_only=True)
    images = BikeImageSerializer(many=True, read_only=True)

    class Meta:
        model = Bike
        fields = [
            'id', 'reg_number', 'brand', 'model_name', 'year', 
            'km_driven', 'expected_price', 'status', 'image', 
            'inspection', 'images'
        ]

class BikeSellRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bike
        fields = ['seller_name', 'seller_phone', 'reg_number', 'brand', 'model_name', 'year', 'km_driven', 'expected_price']

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'