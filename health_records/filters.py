import django_filters
from .models import HealthRecord, Vaccination, Treatment


class HealthRecordFilter(django_filters.FilterSet):
    """Health record filters"""
    
    record_type = django_filters.ChoiceFilter(choices=HealthRecord.RECORD_TYPE_CHOICES)
    priority = django_filters.ChoiceFilter(choices=HealthRecord.PRIORITY_CHOICES)
    is_resolved = django_filters.BooleanFilter()
    visit_date_from = django_filters.DateFilter(field_name='visit_date', lookup_expr='gte')
    visit_date_to = django_filters.DateFilter(field_name='visit_date', lookup_expr='lte')
    animal = django_filters.UUIDFilter(field_name='animal__id')
    
    class Meta:
        model = HealthRecord
        fields = ['record_type', 'priority', 'is_resolved', 'animal']


class VaccinationFilter(django_filters.FilterSet):
    """Vaccination filters"""
    
    status = django_filters.ChoiceFilter(choices=Vaccination.STATUS_CHOICES)
    scheduled_date_from = django_filters.DateFilter(field_name='scheduled_date', lookup_expr='gte')
    scheduled_date_to = django_filters.DateFilter(field_name='scheduled_date', lookup_expr='lte')
    animal = django_filters.UUIDFilter(field_name='animal__id')
    
    class Meta:
        model = Vaccination
        fields = ['status', 'animal']


class TreatmentFilter(django_filters.FilterSet):
    """Treatment filters"""
    
    status = django_filters.ChoiceFilter(choices=Treatment.STATUS_CHOICES)
    frequency = django_filters.ChoiceFilter(choices=Treatment.FREQUENCY_CHOICES)
    animal = django_filters.UUIDFilter(field_name='animal__id')
    
    class Meta:
        model = Treatment
        fields = ['status', 'frequency', 'animal']