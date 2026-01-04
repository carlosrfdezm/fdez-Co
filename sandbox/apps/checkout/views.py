from django.conf import settings
from django.http import JsonResponse
from oscar.apps.checkout import views
from oscar.core.loading import get_model

# SDK nuevo de PayPal
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest

# Configuración del cliente PayPal (sandbox)
environment = SandboxEnvironment(
    client_id=settings.PAYPAL_CLIENT_ID,
    client_secret=settings.PAYPAL_CLIENT_SECRET
)
client = PayPalHttpClient(environment)

# Modelos de Oscar para registrar el pago
PaymentSourceType = get_model('payment', 'SourceType')
PaymentSource = get_model('payment', 'Source')


class PaymentDetailsView(views.PaymentDetailsView):
    template_name = 'oscar/checkout/payment_details.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['PAYPAL_CLIENT_ID'] = settings.PAYPAL_CLIENT_ID
        return ctx

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Caso confirmación de pedido desde preview
        if request.POST.get("action") == "place_order":
            return super().post(request, *args, **kwargs)

        # Caso AJAX desde botón PayPal → crear orden
        basket = self.request.basket
        shipping_address = self.get_shipping_address(basket)
        shipping_method = self.get_shipping_method(basket, shipping_address)
        shipping_charge = shipping_method.calculate(basket)
        order_total = self.get_order_totals(basket, shipping_charge=shipping_charge)

        # Crear orden en PayPal
        create_request = OrdersCreateRequest()
        create_request.prefer("return=representation")
        create_request.request_body({
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": "EUR",
                    "value": "{:.2f}".format(order_total.incl_tax)
                }
            }]
        })

        response = client.execute(create_request)
        order_id = response.result.id

        # Guardamos el ID en sesión para usarlo en handle_payment
        request.session['paypal_order_id'] = order_id

        return JsonResponse({'id': order_id})

    def handle_payment(self, order_number, total, **kwargs):
        order_id = self.request.session.get('paypal_order_id')  # debe coincidir con la clave usada en post()

        if not order_id:
             raise views.PaymentError("No se encontró el ID de la orden de PayPal en la sesión.")

        capture_request = OrdersCaptureRequest(order_id)
        capture_response = client.execute(capture_request)

        if capture_response.result.status == "COMPLETED":
            source_type, _ = PaymentSourceType.objects.get_or_create(name='PayPal')
            source = PaymentSource(
                source_type=source_type,
                amount_allocated=total.incl_tax,
                reference=order_id
            )
            self.add_payment_source(source)
            self.add_payment_event('Settled', total.incl_tax)
        else:
            raise views.PaymentError("Error al procesar el pago con PayPal.")

