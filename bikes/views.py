from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Booking
from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from .models import Bike, InspectionReport, Booking
from .serializers import BikeSellRequestSerializer, BikeCatalogSerializer, BookingSerializer
# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Bike
from .serializers import BikeCatalogSerializer, BikeSellRequestSerializer
from datetime import datetime
from .models import OTPVerification

# 1. Algorithmic Valuation: Age aur KM ke hisaab se tentative price range
@csrf_exempt
@api_view(['POST'])
def calculate_bike_valuation(request):
    data = request.data
    brand = data.get('brand', '')
    model_name = data.get('model_name', '')
    year = int(data.get('year', 2020))
    km_driven = int(data.get('km_driven', 20000))

    # Base price calculation (Average ex-showroom/market benchmark)
    base_price = 85000.0  # Default base price standard 100-125cc bike ke liye

    # Age depreciation (10% per year)
    current_year = datetime.now().year
    age = max(0, current_year - year)
    depreciation_rate = min(0.65, age * 0.09)

    # KM driven factor
    km_penalty = (km_driven / 10000) * 1500

    estimated_fair_price = max(12000, (base_price * (1 - depreciation_rate)) - km_penalty)
    min_range = round(estimated_fair_price * 0.92, -2)
    max_range = round(estimated_fair_price * 1.05, -2)

    return Response({
        "brand": brand,
        "model": model_name,
        "year": year,
        "km_driven": km_driven,
        "estimated_price_range": {
            "min_price": min_range,
            "max_price": max_range,
            "display": f"₹{int(min_range):,} - ₹{int(max_range):,}"
        },
        "message": "Home inspection book karein to lock this price."
    })

# 2. Seller API: Customer bike bechne ke liye submit karega
@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def submit_sell_request(request):
    serializer = BikeSellRequestSerializer(data=request.data)
    if serializer.is_valid():
        bike = serializer.save()
        return Response({
            "status": "SUCCESS",
            "message": "Bike successfully listed! Head Inspector will schedule doorstep inspection.",
            "bike_id": bike.id
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3. Buyer API: Certified & Verified bikes feed
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_verified_catalog(request):
    bikes = Bike.objects.filter(status='VERIFIED')
    serializer = BikeCatalogSerializer(bikes, many=True, context={'request': request})
    return Response({
        "count": len(serializer.data),
        "bikes": serializer.data
    })
def home_page(request):
    return render(request, 'bikes/index.html')

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def book_bike_token(request):
    bike_id = request.data.get('bike_id')
    buyer_name = request.data.get('buyer_name')
    buyer_phone = request.data.get('buyer_phone')
    preferred_slot = request.data.get('preferred_slot', 'Morning (10:00 AM - 01:00 PM)')

    if not bike_id or not buyer_name or not buyer_phone:
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        bike = Bike.objects.get(id=int(bike_id))
    except (Bike.DoesNotExist, ValueError):
        return Response({"error": "Selected bike is not found."}, status=status.HTTP_404_NOT_FOUND)

    booking = Booking.objects.create(
        bike=bike,
        buyer_name=buyer_name,
        buyer_phone=buyer_phone,
        preferred_slot=preferred_slot,
        token_amount=99.00,
        payment_status='PAID'
    )

    return Response({
        "status": "SUCCESS",
        "booking_id": booking.id,
        "message": f"Test ride reserved for {bike.brand} {bike.model_name}! Our team will coordinate your visit."
    }, status=status.HTTP_201_CREATED)

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import random
from .models import OTPVerification

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def send_otp(request):
    phone = request.data.get('phone', '').strip()
    if not phone or len(phone) < 10:
        return Response({"error": "Valid 10-digit phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

    otp = str(random.randint(1000, 9999))
    OTPVerification.objects.create(phone=phone, otp_code=otp)

    print("\n==========================================")
    print(f"🔑 [BIKELY DEV OTP] Phone: {phone} | OTP: {otp}")
    print("==========================================\n")

    return Response({
        "status": "SENT",
        "message": f"OTP sent to {phone}. (Check server terminal in Dev mode)"
    }, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def verify_otp(request):
    phone = request.data.get('phone', '').strip()
    otp = request.data.get('otp', '').strip()

    record = OTPVerification.objects.filter(phone=phone, is_verified=False).order_by('-created_at').first()

    if not record:
        return Response({"error": "No pending OTP request found for this number."}, status=status.HTTP_400_BAD_REQUEST)

    if not record.is_valid():
        return Response({"error": "OTP has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

    if record.otp_code != otp:
        return Response({"error": "Incorrect OTP. Try again."}, status=status.HTTP_400_BAD_REQUEST)

    record.is_verified = True
    record.save()

    return Response({
        "status": "VERIFIED",
        "message": "Phone number successfully verified!"
    }, status=status.HTTP_200_OK)