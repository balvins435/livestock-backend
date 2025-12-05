from rest_framework import serializers
from .models import Animal, Breed, AnimalWeight, AnimalPhoto, AnimalDocument


#  Breed serializer
class BreedSerializer(serializers.ModelSerializer):  
    class Meta:
        model = Breed
        fields = ['id', 'name', 'species', 'description', 'origin', 
                  'average_weight', 'average_lifespan', 'created_at']
        read_only_fields = ['id', 'created_at']


# Weight record serializer
class AnimalWeightSerializer(serializers.ModelSerializer):   
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)
    
    class Meta:
        model = AnimalWeight
        fields = ['id', 'animal', 'weight', 'measured_at', 'notes', 
                  'recorded_by', 'recorded_by_name', 'created_at']
        read_only_fields = ['id', 'created_at', 'recorded_by']


class AnimalPhotoSerializer(serializers.ModelSerializer):
    """Animal photo serializer"""
    
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    
    class Meta:
        model = AnimalPhoto
        fields = ['id', 'animal', 'image', 'caption', 'uploaded_at', 
                  'uploaded_by', 'uploaded_by_name']
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by']


#  Animal document serializer
class AnimalDocumentSerializer(serializers.ModelSerializer):
       
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    
    class Meta:
        model = AnimalDocument
        fields = ['id', 'animal', 'document_type', 'title', 'file', 
                  'description', 'uploaded_at', 'uploaded_by', 'uploaded_by_name']
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by']


# Animal list serializer
class AnimalListSerializer(serializers.ModelSerializer):
        
    breed_name = serializers.CharField(source='breed.name', read_only=True)
    age = serializers.ReadOnlyField()
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    
    class Meta:
        model = Animal
        fields = ['id', 'name', 'tag_id', 'breed_name', 'gender', 'age', 
                  'weight', 'health_status', 'status', 'photo', 'owner_name', 
                  'created_at']
        read_only_fields = ['id', 'created_at', 'age']


# Animal detail serializer
class AnimalDetailSerializer(serializers.ModelSerializer):
        
    breed_details = BreedSerializer(source='breed', read_only=True)
    age = serializers.ReadOnlyField()
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    
    # Lineage
    sire_name = serializers.CharField(source='sire.name', read_only=True)
    dam_name = serializers.CharField(source='dam.name', read_only=True)
    
    # Related data counts
    weight_records_count = serializers.SerializerMethodField()
    photos_count = serializers.SerializerMethodField()
    documents_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Animal
        fields = '__all__'
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at', 'age']
    
    def get_weight_records_count(self, obj):
        return obj.weight_records.count()
    
    def get_photos_count(self, obj):
        return obj.photos.count()
    
    def get_documents_count(self, obj):
        return obj.documents.count()


# Animal create/update serializer
class AnimalCreateUpdateSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = Animal
        fields = ['name', 'tag_id', 'breed', 'gender', 'date_of_birth', 
                  'color', 'weight', 'photo', 'microchip_number', 'sire', 
                  'dam', 'location', 'status', 'health_status', 'purpose', 
                  'notes', 'acquisition_date', 'acquisition_cost']
    
    def validate_tag_id(self, value):
        """Ensure tag_id is unique"""
        instance = self.instance
        if instance and Animal.objects.exclude(pk=instance.pk).filter(tag_id=value).exists():
            raise serializers.ValidationError("An animal with this tag ID already exists.")
        elif not instance and Animal.objects.filter(tag_id=value).exists():
            raise serializers.ValidationError("An animal with this tag ID already exists.")
        return value
    
    def validate(self, attrs):
        """Validate lineage"""
        sire = attrs.get('sire')
        dam = attrs.get('dam')
        
        if sire and sire.gender != 'male':
            raise serializers.ValidationError({"sire": "Sire must be a male animal."})
        
        if dam and dam.gender != 'female':
            raise serializers.ValidationError({"dam": "Dam must be a female animal."})
        
        return attrs