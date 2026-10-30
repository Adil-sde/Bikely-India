from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('valuation/', views.calculate_bike_valuation, name='bike_valuation'),
    path('sell/', views.submit_sell_request, name='bike_sell'),
    path('catalog/', views.get_verified_catalog, name='bike_catalog'),
    path('book-token/', views.book_bike_token, name = 'bike_book'),
    path('api/auth/send-otp/', views.send_otp, name='send_otp'),
    path('api/auth/verify-otp/', views.verify_otp, name='verify_otp'),
]
