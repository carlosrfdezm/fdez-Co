from oscar.apps.catalogue.views import CatalogueView, ProductCategoryView
from oscar.apps.search.views import FacetedSearchView
from oscar.apps.offer.models import ConditionalOffer
from django.utils import timezone

class OffersMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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

        context["offers_with_products"] = offers_with_products
        return context

class CustomCatalogueView(OffersMixin, CatalogueView):
    pass

class CustomCategoryView(OffersMixin, ProductCategoryView):
    pass

class CustomSearchView(OffersMixin, FacetedSearchView):
    pass

