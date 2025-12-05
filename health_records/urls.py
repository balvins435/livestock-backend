from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HealthRecordViewSet, VaccinationViewSet, TreatmentViewSet,
    LabTestViewSet, HealthAlertViewSet
)

router = DefaultRouter()
router.register(r'records', HealthRecordViewSet, basename='health-record')
router.register(r'vaccinations', VaccinationViewSet, basename='vaccination')
router.register(r'treatments', TreatmentViewSet, basename='treatment')
router.register(r'lab-tests', LabTestViewSet, basename='lab-test')
router.register(r'alerts', HealthAlertViewSet, basename='health-alert')

app_name = 'health_records'

urlpatterns = [
    path('', include(router.urls)),
]