from rest_framework import serializers

from .models import *

class ServiceCategorySerializer(serializers.ModelSerializer):
  class Meta :
    model = ServiceCatagory
    fields = ['id' , 'title' , 'photo' , 'description']

class ServiceSerializer(serializers.ModelSerializer):
  class Meta:
    model = Service
    fields = ['id' , 'title' , 'photo' , 'description' , 'catagory']