from rest_framework import serializers
from service.serializers import ServiceSerializer
from user.models import Address
from user.serializers import     AddressSerializer
from .models import Job



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
                  'provider', 'service', 'service_catagory']

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
        instance.complete_date = validated_data.get('complete_date', instance.complete_date)
        instance.flexable = validated_data.get('flexable', instance.flexable)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.is_done = validated_data.get('is_done', instance.is_done)

        instance.save()
        return instance
