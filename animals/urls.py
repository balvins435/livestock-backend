from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnimalViewSet, BreedViewSet

router = DefaultRouter()
router.register(r'animals', AnimalViewSet, basename='animal')
router.register(r'breeds', BreedViewSet, basename='breed')

app_name = 'animals'

urlpatterns = [
    path('', include(router.urls)),
]