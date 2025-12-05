import django_filters
from .models import Animal


class AnimalFilter(django_filters.FilterSet):
    """Custom filters for animals"""
    
    breed = django_filters.CharFilter(field_name='breed__name', lookup_expr='icontains')
    gender = django_filters.ChoiceFilter(choices=Animal.GENDER_CHOICES)
    status = django_filters.ChoiceFilter(choices=Animal.STATUS_CHOICES)
    health_status = django_filters.ChoiceFilter(choices=Animal.HEALTH_STATUS)
    min_weight = django_filters.NumberFilter(field_name='weight', lookup_expr='gte')
    max_weight = django_filters.NumberFilter(field_name='weight', lookup_expr='lte')
    location = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Animal
        fields = ['breed', 'gender', 'status', 'health_status', 'location', 'min_weight', 'max_weight']