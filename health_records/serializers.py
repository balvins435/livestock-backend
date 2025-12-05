from rest_framework import serializers
from .models import HealthRecord, Vaccination, Treatment, LabTest, HealthAlert


class HealthRecordListSerializer(serializers.ModelSerializer):
    """Simplified health record list"""
    
    animal_name = serializers.CharField(source='animal.name', read_only=True)
    animal_tag = serializers.CharField(source='animal.tag_id', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = HealthRecord
        fields = ['id', 'animal', 'animal_name', 'animal_tag', 'record_type', 
                  'title', 'priority', 'is_resolved', 'visit_date', 
                  'veterinarian', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class HealthRecordDetailSerializer(serializers.ModelSerializer):
    """Detailed health record"""
    
    animal_name = serializers.CharField(source='animal.name', read_only=True)
    animal_tag = serializers.CharField(source='animal.tag_id', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = HealthRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'resolved_date']


class HealthRecordCreateUpdateSerializer(serializers.ModelSerializer):
    """Create/Update health record"""
    
    class Meta:
        model = HealthRecord
        fields = ['animal', 'record_type', 'title', 'description', 'diagnosis',
                  'symptoms', 'temperature', 'heart_rate', 'respiratory_rate',
                  'treatment_provided', 'medications', 'priority', 'is_resolved',
                  'veterinarian', 'veterinarian_license', 'visit_date',
                  'follow_up_date', 'cost', 'notes']
    
    def validate_temperature(self, value):
        if value and (value < 95 or value > 110):
            raise serializers.ValidationError("Temperature seems abnormal. Please verify.")
        return value


class VaccinationSerializer(serializers.ModelSerializer):
    """Vaccination serializer"""
    
    animal_name = serializers.CharField(source='animal.name', read_only=True)
    animal_tag = serializers.CharField(source='animal.tag_id', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Vaccination
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class TreatmentSerializer(serializers.ModelSerializer):
    """Treatment serializer"""
    
    animal_name = serializers.CharField(source='animal.name', read_only=True)
    animal_tag = serializers.CharField(source='animal.tag_id', read_only=True)
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Treatment
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class LabTestSerializer(serializers.ModelSerializer):
    """Lab test serializer"""
    
    animal_name = serializers.CharField(source='animal.name', read_only=True)
    animal_tag = serializers.CharField(source='animal.tag_id', read_only=True)
    
    class Meta:
        model = LabTest
        fields = '__all__'
        read_only_fields = ['id', 'requested_by', 'created_at', 'updated_at']


class HealthAlertSerializer(serializers.ModelSerializer):
    """Health alert serializer"""
    
    animal_name = serializers.CharField(source='animal.name', read_only=True)
    animal_tag = serializers.CharField(source='animal.tag_id', read_only=True)
    
    class Meta:
        model = HealthAlert
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'resolved_date']
