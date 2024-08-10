from rest_framework import serializers
from service.serializers import ServiceSerializer
from user.serializers import     AddressSerializer
from .models import Job

class JobSerializer(serializers.ModelSerializer):
  class Meta:
    model = Job
    fields = ['id', 'submit_date' , 'start_date' , 'complete_date' , 'flexable' , 'is_active' , 'address' , 'service']

class ProfessionalJobSerializer(serializers.ModelSerializer):
  service = ServiceSerializer
  # simple_user = UserSerializer
  # professional = ProfessionalSerializer
  # address = AddressSerializer

  class Meta:
    model = Job
    fields = ['id' , 'submit_date' , 'start_date' , 'complete_date' , 
              'flexable' , 'is_active' ,'service' , 'professional' , 
              'provider' , 'address']

