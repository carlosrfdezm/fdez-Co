# sandbox/core/urls.py
from django.urls import path
from .views import CustomHomeView, CustomSearchView

urlpatterns = [
    path("homepage/", CustomHomeView.as_view(), name="homepage"),
    path("search/", CustomSearchView.as_view(), name="search"),
]
