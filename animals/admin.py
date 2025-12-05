from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Animal, Breed, AnimalWeight, AnimalPhoto, AnimalDocument


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ['name', 'species', 'origin', 'average_weight', 'created_at']
    list_filter = ['species']
    search_fields = ['name', 'origin']
    ordering = ['species', 'name']


class AnimalWeightInline(admin.TabularInline):
    model = AnimalWeight
    extra = 1
    readonly_fields = ['created_at']


class AnimalPhotoInline(admin.TabularInline):
    model = AnimalPhoto
    extra = 1
    readonly_fields = ['uploaded_at']


class AnimalDocumentInline(admin.TabularInline):
    model = AnimalDocument
    extra = 1
    readonly_fields = ['uploaded_at']


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['name', 'tag_id', 'breed', 'gender', 'age', 'weight', 
                    'health_status', 'status', 'owner', 'created_at']
    list_filter = ['gender', 'health_status', 'status', 'breed__species']
    search_fields = ['name', 'tag_id', 'owner__email']
    readonly_fields = ['created_at', 'updated_at', 'age']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'name', 'tag_id', 'breed', 'gender', 'date_of_birth', 'age')
        }),
        ('Physical Attributes', {
            'fields': ('color', 'weight', 'photo', 'microchip_number')
        }),
        ('Lineage', {
            'fields': ('sire', 'dam')
        }),
        ('Location & Status', {
            'fields': ('location', 'status', 'health_status', 'purpose')
        }),
        ('Acquisition', {
            'fields': ('acquisition_date', 'acquisition_cost')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [AnimalWeightInline, AnimalPhotoInline, AnimalDocumentInline]


@admin.register(AnimalWeight)
class AnimalWeightAdmin(admin.ModelAdmin):
    list_display = ['animal', 'weight', 'measured_at', 'recorded_by']
    list_filter = ['measured_at']
    search_fields = ['animal__name', 'animal__tag_id']
    readonly_fields = ['created_at']


@admin.register(AnimalPhoto)
class AnimalPhotoAdmin(admin.ModelAdmin):
    list_display = ['animal', 'caption', 'uploaded_at', 'uploaded_by']
    list_filter = ['uploaded_at']
    search_fields = ['animal__name', 'caption']
    readonly_fields = ['uploaded_at']


@admin.register(AnimalDocument)
class AnimalDocumentAdmin(admin.ModelAdmin):
    list_display = ['animal', 'document_type', 'title', 'uploaded_at', 'uploaded_by']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['animal__name', 'title']
    readonly_fields = ['uploaded_at']
