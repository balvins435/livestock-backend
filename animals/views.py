from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Animal, Breed, AnimalWeight, AnimalPhoto, AnimalDocument
from .serializers import (
    AnimalListSerializer, AnimalDetailSerializer, AnimalCreateUpdateSerializer,
    BreedSerializer, AnimalWeightSerializer, AnimalPhotoSerializer, 
    AnimalDocumentSerializer
)
from .filters import AnimalFilter
from users.permissions import IsOwnerOrAdmin, IsFarmerOrAdmin


# Breed CRUD operations
class BreedViewSet(viewsets.ModelViewSet):
    
    queryset = Breed.objects.all()
    serializer_class = BreedSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'species', 'origin']
    filterset_fields = ['species']
    
    def get_permissions(self):
        """Only admins can create/update/delete breeds"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        return [IsAuthenticated()]


class AnimalViewSet(viewsets.ModelViewSet):
    """Animal CRUD operations"""
    
    permission_classes = [IsAuthenticated, IsFarmerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AnimalFilter
    search_fields = ['name', 'tag_id', 'breed__name']
    ordering_fields = ['created_at', 'name', 'date_of_birth', 'weight', 'health_status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Users see only their animals, admins see all"""
        user = self.request.user
        if user.role == 'admin':
            return Animal.objects.select_related('breed', 'owner', 'sire', 'dam').all()
        return Animal.objects.select_related('breed', 'owner', 'sire', 'dam').filter(owner=user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AnimalListSerializer
        elif self.action == 'retrieve':
            return AnimalDetailSerializer
        return AnimalCreateUpdateSerializer
    
    def perform_create(self, serializer):
        """Set owner to current user"""
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['get'])
    def weight_history(self, request, pk=None):
        """Get weight history for an animal"""
        animal = self.get_object()
        weights = animal.weight_records.all()
        serializer = AnimalWeightSerializer(weights, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_weight(self, request, pk=None):
        """Add weight record"""
        animal = self.get_object()
        serializer = AnimalWeightSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(animal=animal, recorded_by=request.user)
            
            # Update animal's current weight
            animal.weight = serializer.validated_data['weight']
            animal.save(update_fields=['weight'])
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def photos(self, request, pk=None):
        """Get all photos for an animal"""
        animal = self.get_object()
        photos = animal.photos.all()
        serializer = AnimalPhotoSerializer(photos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def upload_photo(self, request, pk=None):
        """Upload photo for an animal"""
        animal = self.get_object()
        serializer = AnimalPhotoSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(animal=animal, uploaded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Get all documents for an animal"""
        animal = self.get_object()
        documents = animal.documents.all()
        serializer = AnimalDocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def upload_document(self, request, pk=None):
        """Upload document for an animal"""
        animal = self.get_object()
        serializer = AnimalDocumentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(animal=animal, uploaded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def offspring(self, request, pk=None):
        """Get all offspring of an animal"""
        animal = self.get_object()
        
        if animal.gender == 'male':
            offspring = Animal.objects.filter(sire=animal)
        else:
            offspring = Animal.objects.filter(dam=animal)
        
        serializer = AnimalListSerializer(offspring, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get animal statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_animals': queryset.count(),
            'active': queryset.filter(status='active').count(),
            'by_gender': {
                'male': queryset.filter(gender='male').count(),
                'female': queryset.filter(gender='female').count(),
            },
            'by_health_status': {
                'excellent': queryset.filter(health_status='excellent').count(),
                'good': queryset.filter(health_status='good').count(),
                'fair': queryset.filter(health_status='fair').count(),
                'poor': queryset.filter(health_status='poor').count(),
                'critical': queryset.filter(health_status='critical').count(),
            },
            'by_status': {
                'active': queryset.filter(status='active').count(),
                'sold': queryset.filter(status='sold').count(),
                'deceased': queryset.filter(status='deceased').count(),
                'transferred': queryset.filter(status='transferred').count(),
            }
        }
        
        return Response(stats)