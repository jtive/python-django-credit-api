from django.urls import path
from . import views

app_name = "api"

urlpatterns = [
    # Person endpoints
    path(
        "person/",
        views.PersonListCreateView.as_view(),
        name="person-list-create",
    ),
    path(
        "person/<uuid:pk>/",
        views.PersonDetailView.as_view(),
        name="person-detail",
    ),
    # Address endpoints
    path(
        "address/person/<uuid:person_id>/",
        views.AddressListCreateView.as_view(),
        name="address-list-create",
    ),
    path(
        "address/<uuid:pk>/",
        views.AddressDetailView.as_view(),
        name="address-detail",
    ),
    path(
        "address/<uuid:pk>/unmasked/",
        views.UnmaskedAddressDetailView.as_view(),
        name="address-unmasked",
    ),
    # Credit card endpoints
    path(
        "creditcard/person/<uuid:person_id>/",
        views.CreditCardListCreateView.as_view(),
        name="creditcard-list-create",
    ),
    path(
        "creditcard/<uuid:pk>/",
        views.CreditCardDetailView.as_view(),
        name="creditcard-detail",
    ),
    # Health check endpoints
    path("health/", views.health_check, name="health-check"),
    path("health/ready/", views.readiness_check, name="readiness-check"),
]
