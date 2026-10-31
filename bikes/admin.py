from django.contrib import admin
from django.utils.html import format_html
from .models import Bike, InspectionReport, Booking, BikeImage


class BikeImageInline(admin.TabularInline):
    model = BikeImage
    extra = 10     # Admin page par ek sath 10 photos upload karne ke dabbe dikhenge
    max_num = 10   # Maximum 10 photos allow karega


@admin.register(Bike)
class BikeAdmin(admin.ModelAdmin):
    list_display = ('reg_number', 'brand', 'model_name', 'year', 'expected_price', 'status', 'created_at')
    list_filter = ('status', 'brand', 'year')
    search_fields = ('reg_number', 'model_name', 'brand')
    inlines = [BikeImageInline]  # <-- Yahan photo inline jud gaya


@admin.register(InspectionReport)
class InspectionReportAdmin(admin.ModelAdmin):
    list_display = ('bike', 'inspector_name', 'overall_rating', 'engine_sound', 'inspected_at')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer_name', 'buyer_phone', 'bike', 'preferred_slot', 'payment_status', 'whatsapp_action', 'booked_at')
    list_filter = ('payment_status', 'booked_at')
    search_fields = ('buyer_name', 'buyer_phone', 'bike__reg_number')

    def whatsapp_action(self, obj):
        clean_phone = obj.buyer_phone.replace("+", "").replace(" ", "").strip()
        if not clean_phone.startswith("91") and len(clean_phone) == 10:
            clean_phone = f"91{clean_phone}"
        msg = f"Namaste {obj.buyer_name} ji, Bikely Patna Hub se baat kar rahe hain. Aapne {obj.bike.brand} {obj.bike.model_name} ke test-ride ke liye request kiya hai. Kya hum time confirm karein?"
        encoded_msg = msg.replace(" ", "%20")
        url = f"https://wa.me/{clean_phone}?text={encoded_msg}"
        return format_html('<a href="{}" target="_blank" style="background:#25D366;color:white;padding:4px 8px;border-radius:4px;text-decoration:none;font-weight:bold;font-size:11px;">💬 WhatsApp</a>', url)

    whatsapp_action.short_description = "Quick Contact"