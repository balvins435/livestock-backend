from django.contrib import admin

# Register your models here.
from .models import HealthRecord, Vaccination, Treatment, LabTest, HealthAlert


class VaccinationInline(admin.TabularInline):
    model = Vaccination
    extra = 0
    fields = ['vaccine_name', 'scheduled_date', 'status']


class TreatmentInline(admin.TabularInline):
    model = Treatment
    extra = 0
    fields = ['medication_name', 'start_date', 'status']


class LabTestInline(admin.TabularInline):
    model = LabTest
    extra = 0
    fields = ['test_name', 'test_type', 'status']


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ['animal', 'title', 'record_type', 'priority', 'is_resolved', 
                    'visit_date', 'veterinarian', 'created_at']
    list_filter = ['record_type', 'priority', 'is_resolved', 'visit_date']
    search_fields = ['animal__name', 'animal__tag_id', 'title', 'diagnosis']
    readonly_fields = ['created_at', 'updated_at', 'resolved_date']
    
    fieldsets = (
        ('Animal & Type', {
            'fields': ('animal', 'record_type', 'title', 'priority')
        }),
        ('Medical Details', {
            'fields': ('description', 'diagnosis', 'symptoms', 'temperature', 
                      'heart_rate', 'respiratory_rate')
        }),
        ('Treatment', {
            'fields': ('treatment_provided', 'medications')
        }),
        ('Veterinarian', {
            'fields': ('veterinarian', 'veterinarian_license')
        }),
        ('Dates & Status', {
            'fields': ('visit_date', 'follow_up_date', 'is_resolved', 'resolved_date')
        }),
        ('Financial', {
            'fields': ('cost',)
        }),
        ('Additional', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [VaccinationInline, TreatmentInline, LabTestInline]


@admin.register(Vaccination)
class VaccinationAdmin(admin.ModelAdmin):
    list_display = ['animal', 'vaccine_name', 'scheduled_date', 'status', 
                    'administered_date', 'next_due_date']
    list_filter = ['status', 'scheduled_date']
    search_fields = ['animal__name', 'vaccine_name', 'disease_target']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ['animal', 'medication_name', 'frequency', 'start_date', 
                    'end_date', 'status']
    list_filter = ['status', 'frequency', 'start_date']
    search_fields = ['animal__name', 'medication_name', 'active_ingredient']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ['animal', 'test_name', 'test_type', 'status', 
                    'requested_date', 'completed_date']
    list_filter = ['test_type', 'status', 'is_normal']
    search_fields = ['animal__name', 'test_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(HealthAlert)
class HealthAlertAdmin(admin.ModelAdmin):
    list_display = ['animal', 'title', 'alert_type', 'severity', 
                    'is_read', 'is_resolved', 'alert_date']
    list_filter = ['alert_type', 'severity', 'is_read', 'is_resolved']
    search_fields = ['animal__name', 'title', 'message']