from rest_framework import serializers
from service.serializers import ServiceSerializer
from user.models import Address
from user.serializers import     AddressSerializer
from .models import Job, JobAcception



class ProfessionalJobSerializer(serializers.ModelSerializer):
  service = ServiceSerializer
  # simple_user = UserSerializer
  # professional = ProfessionalSerializer
  # address = AddressSerializer
 
  class Meta:
    model = Job
    fields = ['id' , 'submit_date' , 'start_date' , 'complete_date' , 
              'flexable' , 'is_active' ,'service'  , 
              'provider' , 'address']
class JobSerializer(serializers.ModelSerializer):
    address = AddressSerializer()  # Nested address serializer
    service = ServiceSerializer(read_only=True)
    
    class Meta:
        model = Job
        fields = ['id', 'submit_date', 'start_date', 'complete_date', 'flexable', 
                  'is_active', 'is_avialable', 'is_done', 'address', 
                  'provider', 'service']

    def create(self, validated_data):
        # Extract the nested address data
        address_data = validated_data.pop('address')

        # Create or get the address based on the provided data
        address, created = Address.objects.get_or_create(
            street=address_data['street'],
            unit_suite=address_data.get('unit_suite'),
            city_id=address_data['city']['id']
        )

        # Automatically assign the provider and other fields
        validated_data['is_avialable'] = True
        validated_data['provider'] = self.context['request'].user
        validated_data['address'] = address

        flexable = validated_data.get('flexable', False)
        if flexable:
            validated_data['start_date'] = None

        # Create the job
        validated_data['complete_date'] = None
        validated_data['is_active'] = False
        validated_data['is_done'] = False
        return Job.objects.create(**validated_data)

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        if address_data:
            # Check if address exists or create a new one
            address, created = Address.objects.get_or_create(
                street=address_data['street'],
                unit_suite=address_data.get('unit_suite'),
                city_id=address_data['city']['id']
            )
            instance.address = address

        # Update job fields
        instance.submit_date = validated_data.get('submit_date', instance.submit_date)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.complete_date = None
        instance.flexable = validated_data.get('flexable', instance.flexable)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.is_done = validated_data.get('is_done', instance.is_done)

        instance.save()
        return instance


class JobAcceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAcception
        fields = ['job', 'professional']

    def create(self, validated_data):
        # Get the related job from validated data
        job = validated_data['job']

        # Update the job status when accepted
        job.is_active = True
        job.is_avialable = False
        job.save()

        # Create the JobAcception instance
        return JobAcception.objects.create(**validated_data)
    


class JobCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['is_done', 'is_active', 'flexable', 'start_date', 'complete_date']

    def validate(self, data):
        # Check if the job is flexible (flexable = True)
        flexable = data.get('flexable', False)
        
        if flexable:
            # If flexable is True, ensure both start_date and complete_date are provided
            if not data.get('start_date'):
                raise serializers.ValidationError("For flexible jobs, 'start_date' must be provided.")
            if not data.get('complete_date'):
                raise serializers.ValidationError("For flexible jobs, 'complete_date' must be provided.")
        else:
            # If flexable is False, only the start_date should be provided
            if not data.get('start_date'):
                raise serializers.ValidationError("For non-flexible jobs, 'start_date' must be provided.")
            # Ensure complete_date is None for non-flexible jobs
            data['complete_date'] = None

        return data

    def update(self, instance, validated_data):
        # Set is_done to True and is_active to False
        instance.is_done = True
        instance.is_active = False

        # Update start_date and complete_date if they exist in validated data
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.complete_date = validated_data.get('complete_date', instance.complete_date)

        # Save the updated instance
        instance.save()
        return instance