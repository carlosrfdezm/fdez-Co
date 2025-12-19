from oscar.apps.checkout.apps import CheckoutConfig

class PaymentsCheckoutConfig(CheckoutConfig):
    name = 'payments'
    label = 'checkout'  # 👈 esto indica que reemplaza la app checkout de Oscar
