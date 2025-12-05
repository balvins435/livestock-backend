from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class HealthRecord(models.Model):
    """Main health record model"""
    
    RECORD_TYPE_CHOICES = [
        ('checkup', 'General Checkup'),
        ('vaccination', 'Vaccination'),
        ('treatment', 'Treatment'),
        ('surgery', 'Surgery'),
        ('injury', 'Injury'),
        ('illness', 'Illness'),
        ('test', 'Laboratory Test'),
        ('other', 'Other'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey('animals.Animal', on_delete=models.CASCADE, related_name='health_records')
    
    # Record details
    record_type = models.CharField(max_length=20, choices=RECORD_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    diagnosis = models.TextField(blank=True)
    
    # Medical details
    symptoms = models.JSONField(default=list, blank=True, help_text="List of symptoms")
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="Temperature in °F")
    heart_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Beats per minute")
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Breaths per minute")
    
    # Treatment
    treatment_provided = models.TextField(blank=True)
    medications = models.JSONField(default=list, blank=True, help_text="List of medications")
    
    # Priority & Status
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_resolved = models.BooleanField(default=False)
    
    # Personnel
    veterinarian = models.CharField(max_length=200, blank=True)
    veterinarian_license = models.CharField(max_length=100, blank=True)
    
    # Dates
    visit_date = models.DateTimeField(default=timezone.now)
    follow_up_date = models.DateField(null=True, blank=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    
    # Cost
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='health_records_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-visit_date']
        indexes = [
            models.Index(fields=['animal', '-visit_date']),
            models.Index(fields=['record_type']),
            models.Index(fields=['priority']),
            models.Index(fields=['is_resolved']),
        ]
    
    def __str__(self):
        return f"{self.animal.name} - {self.title} ({self.visit_date.date()})"
    
    def save(self, *args, **kwargs):
        if self.is_resolved and not self.resolved_date:
            self.resolved_date = timezone.now()
        super().save(*args, **kwargs)


class Vaccination(models.Model):
    """Vaccination records"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey('animals.Animal', on_delete=models.CASCADE, related_name='vaccinations')
    health_record = models.ForeignKey(HealthRecord, on_delete=models.SET_NULL, null=True, blank=True, related_name='vaccinations')
    
    # Vaccine details
    vaccine_name = models.CharField(max_length=200)
    disease_target = models.CharField(max_length=200, help_text="Disease being prevented")
    manufacturer = models.CharField(max_length=200, blank=True)
    batch_number = models.CharField(max_length=100, blank=True)
    
    # Dosage
    dosage = models.CharField(max_length=100)
    administration_route = models.CharField(max_length=100, help_text="e.g., Intramuscular, Subcutaneous")
    
    # Dates
    administered_date = models.DateField(null=True, blank=True)
    scheduled_date = models.DateField()
    next_due_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Personnel
    administered_by = models.CharField(max_length=200, blank=True)
    veterinarian = models.CharField(max_length=200, blank=True)
    
    # Reactions
    adverse_reactions = models.TextField(blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['animal', '-scheduled_date']),
            models.Index(fields=['status']),
            models.Index(fields=['next_due_date']),
        ]
    
    def __str__(self):
        return f"{self.animal.name} - {self.vaccine_name} ({self.scheduled_date})"
    
    @property
    def is_overdue(self):
        if self.status == 'completed':
            return False
        return timezone.now().date() > self.scheduled_date


class Treatment(models.Model):
    """Treatment and medication records"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('discontinued', 'Discontinued'),
    ]
    
    FREQUENCY_CHOICES = [
        ('once', 'Once'),
        ('daily', 'Daily'),
        ('twice_daily', 'Twice Daily'),
        ('three_times_daily', 'Three Times Daily'),
        ('weekly', 'Weekly'),
        ('as_needed', 'As Needed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey('animals.Animal', on_delete=models.CASCADE, related_name='treatments')
    health_record = models.ForeignKey(HealthRecord, on_delete=models.SET_NULL, null=True, blank=True, related_name='treatments')
    
    # Medication details
    medication_name = models.CharField(max_length=200)
    active_ingredient = models.CharField(max_length=200, blank=True)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    administration_route = models.CharField(max_length=100)
    
    # Duration
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    duration_days = models.PositiveIntegerField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Instructions
    instructions = models.TextField(help_text="Administration instructions")
    side_effects = models.TextField(blank=True)
    precautions = models.TextField(blank=True)
    
    # Cost
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Personnel
    prescribed_by = models.CharField(max_length=200)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['animal', '-start_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.animal.name} - {self.medication_name}"
    
    @property
    def is_active(self):
        if self.status != 'active':
            return False
        if self.end_date:
            return timezone.now().date() <= self.end_date
        return True


class LabTest(models.Model):
    """Laboratory test records"""
    
    TEST_TYPE_CHOICES = [
        ('blood', 'Blood Test'),
        ('urine', 'Urine Test'),
        ('fecal', 'Fecal Test'),
        ('biopsy', 'Biopsy'),
        ('xray', 'X-Ray'),
        ('ultrasound', 'Ultrasound'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey('animals.Animal', on_delete=models.CASCADE, related_name='lab_tests')
    health_record = models.ForeignKey(HealthRecord, on_delete=models.SET_NULL, null=True, blank=True, related_name='lab_tests')
    
    # Test details
    test_type = models.CharField(max_length=20, choices=TEST_TYPE_CHOICES)
    test_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Results
    results = models.TextField(blank=True)
    results_file = models.FileField(upload_to='health_records/lab_results/', blank=True, null=True)
    interpretation = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_normal = models.BooleanField(null=True, blank=True)
    
    # Dates
    requested_date = models.DateTimeField(default=timezone.now)
    sample_collected_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    # Laboratory
    laboratory_name = models.CharField(max_length=200, blank=True)
    technician_name = models.CharField(max_length=200, blank=True)
    
    # Cost
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Metadata
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-requested_date']
        indexes = [
            models.Index(fields=['animal', '-requested_date']),
            models.Index(fields=['test_type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.animal.name} - {self.test_name}"


class HealthAlert(models.Model):
    """Health alerts and reminders"""
    
    ALERT_TYPE_CHOICES = [
        ('vaccination_due', 'Vaccination Due'),
        ('checkup_due', 'Checkup Due'),
        ('treatment_due', 'Treatment Due'),
        ('follow_up', 'Follow-up Required'),
        ('abnormal_vitals', 'Abnormal Vitals'),
        ('weight_loss', 'Weight Loss'),
        ('other', 'Other'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey('animals.Animal', on_delete=models.CASCADE, related_name='health_alerts')
    health_record = models.ForeignKey(HealthRecord, on_delete=models.CASCADE, null=True, blank=True, related_name='alerts')
    
    # Alert details
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    
    # Dates
    alert_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-alert_date']
        indexes = [
            models.Index(fields=['animal', '-alert_date']),
            models.Index(fields=['severity']),
            models.Index(fields=['is_resolved']),
        ]
    
    def __str__(self):
        return f"{self.animal.name} - {self.title}"