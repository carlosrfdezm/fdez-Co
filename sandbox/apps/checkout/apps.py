from django.conf import settings
from oscar.apps.checkout import apps as checkout_apps
import paypalrestsdk

class CheckoutConfig(checkout_apps.CheckoutConfig):
    name = 'sandbox.apps.checkout'
    label = 'checkout'  # Oscar buscará este label para reemplazar su propia configuración

    def ready(self):
        super().ready()
# Configuración del SDK al iniciar la app
        paypalrestsdk.configure({
            "mode": settings.PAYPAL_MODE,
            "client_id": settings.PAYPAL_CLIENT_ID,
            "client_secret": settings.PAYPAL_CLIENT_SECRET 
        })

        from .views import PaymentDetailsView
        self.payment_details_view = PaymentDetailsView