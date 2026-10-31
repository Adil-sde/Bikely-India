from django.db import models

class Bike(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Inspection'),
        ('VERIFIED', 'Verified & Ready for Sale'),
        ('BOOKED', 'Booked / Token Paid'),
        ('SOLD', 'Sold'),
    ]

    seller_name = models.CharField(max_length=100)
    seller_phone = models.CharField(max_length=15)
    reg_number = models.CharField(max_length=20, unique=True)
    brand = models.CharField(max_length=50)        # Hero, Honda, TVS, Bajaj, etc.
    model_name = models.CharField(max_length=100)  # Splendor Plus, Activa 6G, etc.
    year = models.PositiveIntegerField()
    km_driven = models.PositiveIntegerField()
    expected_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='bikes/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} {self.model_name} ({self.reg_number})"


class InspectionReport(models.Model):
    NOISE_CHOICES = [
        ('NORMAL', 'Smooth / Normal Engine Sound'),
        ('TAPPET', 'Mild Tappet Noise'),
        ('PISTON', 'Heavy Piston / Piston Ring Sound'),
    ]

    SMOKE_CHOICES = [
        ('CLEAN', 'No Smoke (Clean Exhaust)'),
        ('WHITE', 'White Smoke (Oil Burning)'),
        ('BLACK', 'Black Smoke (Rich Fuel/Carb Issue)'),
    ]

    bike = models.OneToOneField(Bike, on_delete=models.CASCADE, related_name='inspection')
    inspector_name = models.CharField(max_length=100, default="Head Inspector")
    
    # 5-Pillar Score (1.0 se 5.0 tak)
    engine_score = models.FloatField(default=5.0)
    chassis_score = models.FloatField(default=5.0)
    electrical_score = models.FloatField(default=5.0)
    tyre_score = models.FloatField(default=5.0)
    overall_rating = models.FloatField(default=5.0)

    # Diagnostics
    engine_sound = models.CharField(max_length=20, choices=NOISE_CHOICES, default='NORMAL')
    smoke_test = models.CharField(max_length=20, choices=SMOKE_CHOICES, default='CLEAN')
    meter_tampered = models.BooleanField(default=False)
    estimated_refurb_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    mechanic_notes = models.TextField(blank=True, null=True)
    inspected_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.overall_rating = round((self.engine_score + self.chassis_score + self.electrical_score + self.tyre_score) / 4.0, 1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Report for {self.bike.reg_number} - Score: {self.overall_rating}/5.0"

class Booking(models.Model):
    bike = models.ForeignKey(Bike, on_delete=models.CASCADE, related_name='bookings')
    buyer_name = models.CharField(max_length=100)
    buyer_phone = models.CharField(max_length=15)
    preferred_slot = models.CharField(max_length=50)
    token_amount = models.DecimalField(max_digits=10, decimal_places=2, default=999.00)
    payment_status = models.CharField(max_length=20, default='PAID')
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking #{self.id} - {self.buyer_name} ({self.bike.brand} {self.bike.model_name})"

    import random
from django.utils import timezone
from datetime import timedelta

class OTPVerification(models.Model):
    phone = models.CharField(max_length=15, db_index=True)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_valid(self):
        # OTP 5 minute ke liye valid rahega
        return timezone.now() < self.created_at + timedelta(minutes=5)

    def __str__(self):
        return f"{self.phone} - {self.otp_code} ({'Verified' if self.is_verified else 'Pending'})"

class BikeImage(models.Model):
    bike = models.ForeignKey('Bike', related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='bikes/gallery/')
    caption = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.bike} Image"