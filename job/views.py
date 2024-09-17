from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import filters
from .models import Job

from .serializers import JobSerializer , ProfessionalJobSerializer
# Create your views here.

class JobListView(APIView):
  def get(self , request , format = None):
    jobs = Job.objects.all()
    serializer = JobSerializer(jobs , many = True)
    return Response(serializer.data)
  def post(self,request , format = None):
    serializer = JobSerializer(data = request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data , status= status.HTTP_201_CREATED)
    return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)

class JobDetailView(generics.RetrieveAPIView):
  queryset = Job.objects.all()
  serializer_class = JobSerializer
  def retrieve(self, request , *args , **kwargs):
    instance = self.get_object()
    serializer = self.get_serializer(instance)
    return Response(serializer.data)
  
class CompletedJobView(generics.ListAPIView):
  queryset = Job.objects.filter(is_active = False)
  serializer_class = JobSerializer

class ProfessionalJobListView(generics.ListAPIView):
  serializer_class = ProfessionalJobSerializer

  def get_queryset(self):
    user_id = self.kwargs['user_id']
    return Job.objects.filter(professional__id = user_id)
  
class ProfessionalCompletedJobListView(generics.ListAPIView):
  serializer_class = ProfessionalJobSerializer

  def get_queryset(self):
    user_id = self.kwargs['user_id']
    return Job.objects.filter(professional__id = user_id , is_active = False)
class CreateJobCreateUpdateView(generics.ListCreateAPIView):