from django.urls import path
from .views import PaypalCheckoutView, success_view, cancel_view

urlpatterns = [
    path('checkout/paypal/', PaypalCheckoutView.as_view(), name='paypal_checkout'),
    path('payment/success/', success_view, name='paypal_success'),
    path('payment/cancel/', cancel_view, name='paypal_cancel'),
]
