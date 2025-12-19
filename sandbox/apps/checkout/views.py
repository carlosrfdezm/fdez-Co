import paypalrestsdk
from django.conf import settings
from django.shortcuts import redirect
from oscar.apps.checkout import views
from oscar.core.loading import get_model

from django.http import JsonResponse
import json



# Cargamos modelos de Oscar para registrar el pago después
PaymentSourceType = get_model('payment', 'SourceType')
PaymentSource = get_model('payment', 'Source')

class PaymentDetailsView(views.PaymentDetailsView):
    template_name = 'oscar/checkout/payment_details.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['PAYPAL_CLIENT_ID'] = settings.PAYPAL_CLIENT_ID
        return ctx

    def get(self, request, *args, **kwargs):
        # Esto lanzará un error que veremos en el navegador
        # Confirmando que Django POR FIN entró a tu archivo.
        
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        basket = self.request.basket
        
        # 1. Obtenemos el método de envío y la dirección para calcular el costo
        shipping_address = self.get_shipping_address(basket)
        shipping_method = self.get_shipping_method(basket, shipping_address)
        shipping_charge = shipping_method.calculate(basket)

        # 2. Ahora pasamos el shipping_charge al total
        order_total = self.get_order_totals(basket, shipping_charge=shipping_charge)

        # 3. Configuramos el pago en PayPal usando el total correcto
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": request.build_absolute_uri('/checkout/preview/'),
                "cancel_url": request.build_absolute_uri('/checkout/payment-details/'),
            },
            "transactions": [{
                "amount": {
                    "total": "{:.2f}".format(order_total.incl_tax),
                    "currency": "EUR"
                },
                "description": f"Pedido {basket.id}"
            }]
        })

        if payment.create():
            # EN LUGAR DE REDIRECT, DEVOLVEMOS EL ID
            return JsonResponse({'id': payment.id})
        
        return JsonResponse({'error': 'No se pudo crear el pago'}, status=400)

    def handle_payment(self, order_number, total, **kwargs):
        # Este método se ejecuta al confirmar el pedido final
        payment_id = self.request.session.get('paypal_payment_id')
        payer_id = self.request.GET.get('PayerID')
        
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            source_type, _ = PaymentSourceType.objects.get_or_create(name='PayPal')
            source = PaymentSource(source_type=source_type, amount_allocated=total.incl_tax, reference=payment_id)
            self.add_payment_source(source)
            self.add_payment_event('Settled', total.incl_tax)
        else:
            raise views.PaymentError("Error al procesar el pago con PayPal.")