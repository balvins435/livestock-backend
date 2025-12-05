from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count

from .models import HealthRecord, Vaccination, Treatment, LabTest, HealthAlert
from .serializers import (
    HealthRecordListSerializer, HealthRecordDetailSerializer,
    HealthRecordCreateUpdateSerializer, VaccinationSerializer,
    TreatmentSerializer, LabTestSerializer, HealthAlertSerializer
)
from .filters import HealthRecordFilter, VaccinationFilter, TreatmentFilter
from users.permissions import IsFarmerOrAdmin


class HealthRecordViewSet(viewsets.ModelViewSet):
    """Health record CRUD operations"""
    
    permission_classes = [IsAuthenticated, IsFarmerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = HealthRecordFilter
    search_fields = ['title', 'diagnosis', 'animal__name', 'animal__tag_id']
    ordering_fields = ['visit_date', 'created_at', 'priority']
    ordering = ['-visit_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return HealthRecord.objects.select_related('animal', 'created_by').all()
        return HealthRecord.objects.select_related('animal', 'created_by').filter(animal__owner=user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return HealthRecordListSerializer
        elif self.action == 'retrieve':
            return HealthRecordDetailSerializer
        return HealthRecordCreateUpdateSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_resolved(self, request, pk=None):
        """Mark health record as resolved"""
        record = self.get_object()
        record.is_resolved = True
        record.resolved_date = timezone.now()
        record.save()
        
        return Response({'message': 'Health record marked as resolved'})
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get health record statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_records': queryset.count(),
            'by_type': {
                'checkup': queryset.filter(record_type='checkup').count(),
                'vaccination': queryset.filter(record_type='vaccination').count(),
                'treatment': queryset.filter(record_type='treatment').count(),
                'surgery': queryset.filter(record_type='surgery').count(),
                'injury': queryset.filter(record_type='injury').count(),
                'illness': queryset.filter(record_type='illness').count(),
            },
            'by_priority': {
                'low': queryset.filter(priority='low').count(),
                'medium': queryset.filter(priority='medium').count(),
                'high': queryset.filter(priority='high').count(),
                'critical': queryset.filter(priority='critical').count(),
            },
            'resolved': queryset.filter(is_resolved=True).count(),
            'unresolved': queryset.filter(is_resolved=False).count(),
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent health records"""
        queryset = self.get_queryset()[:10]
        serializer = HealthRecordListSerializer(queryset, many=True)
        return Response(serializer.data)


class VaccinationViewSet(viewsets.ModelViewSet):
    """Vaccination CRUD operations"""
    
    serializer_class = VaccinationSerializer
    permission_classes = [IsAuthenticated, IsFarmerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = VaccinationFilter
    search_fields = ['vaccine_name', 'disease_target', 'animal__name']
    ordering_fields = ['scheduled_date', 'administered_date']
    ordering = ['-scheduled_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Vaccination.objects.select_related('animal').all()
        return Vaccination.objects.select_related('animal').filter(animal__owner=user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming vaccinations"""
        queryset = self.get_queryset().filter(
            status='scheduled',
            scheduled_date__gte=timezone.now().date()
        ).order_by('scheduled_date')[:10]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue vaccinations"""
        queryset = self.get_queryset().filter(
            status='scheduled',
            scheduled_date__lt=timezone.now().date()
        ).order_by('scheduled_date')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark vaccination as completed"""
        vaccination = self.get_object()
        vaccination.status = 'completed'
        vaccination.administered_date = timezone.now().date()
        vaccination.save()
        
        return Response({'message': 'Vaccination marked as completed'})


class TreatmentViewSet(viewsets.ModelViewSet):
    """Treatment CRUD operations"""
    
    serializer_class = TreatmentSerializer
    permission_classes = [IsAuthenticated, IsFarmerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TreatmentFilter
    search_fields = ['medication_name', 'active_ingredient', 'animal__name']
    ordering_fields = ['start_date', 'end_date']
    ordering = ['-start_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Treatment.objects.select_related('animal').all()
        return Treatment.objects.select_related('animal').filter(animal__owner=user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active treatments"""
        queryset = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark treatment as completed"""
        treatment = self.get_object()
        treatment.status = 'completed'
        treatment.end_date = timezone.now().date()
        treatment.save()
        
        return Response({'message': 'Treatment marked as completed'})


class LabTestViewSet(viewsets.ModelViewSet):
    """Lab test CRUD operations"""
    
    serializer_class = LabTestSerializer
    permission_classes = [IsAuthenticated, IsFarmerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['test_name', 'test_type', 'animal__name']
    ordering_fields = ['requested_date', 'completed_date']
    ordering = ['-requested_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return LabTest.objects.select_related('animal').all()
        return LabTest.objects.select_related('animal').filter(animal__owner=user)
    
    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending lab tests"""
        queryset = self.get_queryset().filter(status__in=['pending', 'in_progress'])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class HealthAlertViewSet(viewsets.ModelViewSet):
    """Health alert CRUD operations"""
    
    serializer_class = HealthAlertSerializer
    permission_classes = [IsAuthenticated, IsFarmerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'message', 'animal__name']
    ordering_fields = ['alert_date', 'severity']
    ordering = ['-alert_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return HealthAlert.objects.select_related('animal').all()
        return HealthAlert.objects.select_related('animal').filter(animal__owner=user)
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread alerts"""
        queryset = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark alert as read"""
        alert = self.get_object()
        alert.is_read = True
        alert.save()
        
        return Response({'message': 'Alert marked as read'})
    
    @action(detail=True, methods=['post'])
    def mark_resolved(self, request, pk=None):
        """Mark alert as resolved"""
        alert = self.get_object()
        alert.is_resolved = True
        alert.resolved_date = timezone.now()
        alert.save()
        
        return Response({'message': 'Alert marked as resolved'})

