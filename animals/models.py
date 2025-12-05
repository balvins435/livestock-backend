from django.db import models

# Create your models here.
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid

# Animal breeds catalog
class Breed(models.Model):
    
    SPECIES_CHOICES = [
        ('cattle', 'Cattle'),
        ('goat', 'Goat'),
        ('sheep', 'Sheep'),
        ('pig', 'Pig'),
        ('poultry', 'Poultry'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES)
    description = models.TextField(blank=True)
    origin = models.CharField(max_length=100, blank=True)
    
    # Characteristics
    average_weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    average_lifespan = models.PositiveIntegerField(help_text="In years", null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['species', 'name']
        unique_together = ['name', 'species']
        indexes = [
            models.Index(fields=['species']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.species})"


class Animal(models.Model):
    """Main animal model"""
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    HEALTH_STATUS = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('deceased', 'Deceased'),
        ('transferred', 'Transferred'),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='animals')
    
    # Basic information
    name = models.CharField(max_length=100)
    tag_id = models.CharField(max_length=50, unique=True, help_text="Unique identification tag")
    breed = models.ForeignKey(Breed, on_delete=models.SET_NULL, null=True, related_name='animals')
    
    # Physical attributes
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    color = models.CharField(max_length=50, blank=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], help_text="Weight in kg")
    
    # Identification
    photo = models.ImageField(upload_to='animals/photos/', blank=True, null=True)
    microchip_number = models.CharField(max_length=50, blank=True, unique=True, null=True)
    
    # Lineage
    sire = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='offspring_as_father')
    dam = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='offspring_as_mother')
    
    # Location & Status
    location = models.CharField(max_length=200, help_text="Pen/Paddock/Barn location")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    health_status = models.CharField(max_length=20, choices=HEALTH_STATUS, default='good')
    
    # Production (for dairy/meat animals)
    purpose = models.CharField(max_length=100, blank=True, help_text="Dairy, Meat, Breeding, etc.")
    
    # Additional info
    notes = models.TextField(blank=True)
    acquisition_date = models.DateField(default=timezone.now)
    acquisition_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['tag_id']),
            models.Index(fields=['breed']),
            models.Index(fields=['health_status']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.tag_id})"
    
    @property
    def age(self):
        """Calculate age in years and months"""
        today = timezone.now().date()
        years = today.year - self.date_of_birth.year
        months = today.month - self.date_of_birth.month
        
        if months < 0:
            years -= 1
            months += 12
        
        return f"{years}y {months}m"
    
    @property
    def is_active(self):
        return self.status == 'active'


class AnimalWeight(models.Model):
    """Track weight history"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='weight_records')
    weight = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    measured_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-measured_at']
        indexes = [
            models.Index(fields=['animal', '-measured_at']),
        ]
    
    def __str__(self):
        return f"{self.animal.name} - {self.weight}kg on {self.measured_at.date()}"


class AnimalPhoto(models.Model):
    """Multiple photos per animal"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='animals/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Photo of {self.animal.name}"


class AnimalDocument(models.Model):
    """Store animal-related documents"""
    
    DOCUMENT_TYPES = [
        ('certificate', 'Birth Certificate'),
        ('pedigree', 'Pedigree'),
        ('registration', 'Registration Papers'),
        ('medical', 'Medical Records'),
        ('purchase', 'Purchase Agreement'),
        ('insurance', 'Insurance Documents'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='animals/documents/')
    description = models.TextField(blank=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.animal.name}"