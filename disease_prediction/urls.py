from django.urls import path
from .views import DiseasePredictionAPI

urlpatterns = [
    path("predict/", DiseasePredictionAPI.as_view(), name="predict-disease"),
]
