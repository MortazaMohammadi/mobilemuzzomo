from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics , filters
from rest_framework import status

from .serializers import *
from .models import *

class ServiceSearchListView(generics.ListAPIView):
  queryset = Service.objects.all()
  serializer_class = ServiceSerializer
  filter_backends = [filters.SearchFilter]
  search_fields = ['title' , 'catagory__title']

  def get_queryset(self):
    return super().get_queryset()
    query = self.request.query_params.get('query' , None)
    if query is not None:
      queryset = queryset.filter(title__icontains=query)
    return queryset
  
class ServiceListView(APIView):
  def get(self , request , format = None):
    services = Service.objects.all()
    serializer = ServiceSerializer(services , many = True)
    return Response(serializer.data)
  def post(self, request , format = None):
    serializer = ServiceSerializer(data = request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data , status=status.HTTP_201_CREATED)
    return Response(serializer.errors , status= status.HTTP_400_BAD_REQUEST)

class ServiceCatagoryListView(APIView):
  def get(self , request , format = None):
    service_catagories = ServiceCatagory.objects.all()
    serializer = ServiceCategorySerializer(service_catagories , many = True)
    return Response (serializer.data)
  
  def post(self , request , format = None):
    serializer = ServiceCategorySerializer(data = request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data , status=status.HTTP_201_CREATED)
    return Response(serializer.errors , status= status.HTTP_400_BAD_REQUEST)

class ThreeMostVisitedServicesListView(generics.ListAPIView):
  queryset = Service.objects.all()[:3]
  serializer_class = ServiceSerializer

class ServiceDetailView(generics.RetrieveAPIView):
  queryset = Service.objects.all()
  serializer_class = ServiceSerializer
  def retieve(self , request , *args , **kwargs):
    instance = self.get_object()
    serializer = self.get_serializer(instance)
    return Response(serializer.data)

