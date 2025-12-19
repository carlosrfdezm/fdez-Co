import paypalrestsdk
from django.shortcuts import redirect
from django.views import View
from django.http import HttpResponse


def success_view(request):
    payment_id = request.GET.get("paymentId")
    payer_id = request.GET.get("PayerID")

    if payment_id and payer_id:
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            return HttpResponse("✅ Pago completado con éxito")
        else:
            return HttpResponse("❌ Error al procesar el pago")
    return HttpResponse("❌ Parámetros inválidos en la respuesta de PayPal")


def cancel_view(request):
    return HttpResponse("❌ El pago fue cancelado por el usuario")




class PaypalCheckoutView(View):
    def get(self, request, *args, **kwargs):
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": "http://localhost:8000/payment/success/",
                "cancel_url": "http://localhost:8000/payment/cancel/"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "Producto de prueba",
                        "sku": "12345",
                        "price": "10.00",
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": "10.00",
                    "currency": "USD"
                },
                "description": "Compra de prueba con PayPal"
            }]
        })

        if payment.create():
            # Redirige al usuario a PayPal
            for link in payment.links:
                if link.rel == "approval_url":
                    return redirect(link.href)
        else:
            return redirect("/payment/error/")
