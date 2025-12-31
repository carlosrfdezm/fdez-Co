from oscar.apps.offer.models import ConditionalOffer
from django.utils import timezone

def offers_processor(request):
    now = timezone.now()
    offers = ConditionalOffer.objects.filter(
        status="Open",
        start_datetime__lte=now
    ).filter(
        end_datetime__isnull=True
    ) | ConditionalOffer.objects.filter(
        status="Open",
        start_datetime__lte=now,
        end_datetime__gte=now
    )

    offers_with_products = []
    for offer in offers:
        products = []
        if offer.benefit and offer.benefit.range:
            products = list(offer.benefit.range.all_products())
        offers_with_products.append({
            "offer": offer,
            "products": products
        })

    return {"offers_with_products": offers_with_products}
