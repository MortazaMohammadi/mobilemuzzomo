from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import filters
from user.pormissions import IsProfessionalUser
from .models import Job, JobAcception
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly

from .serializers import JobAcceptionSerializer, JobCompletionSerializer, JobSerializer , ProfessionalJobSerializer
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



class JobCreateUpdateView(generics.RetrieveUpdateAPIView, generics.CreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    lookup_field = 'pk'  # This is used for updating the job by its primary key
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_object(self):
        """Override get_object to handle the case where the object doesn't exist for creation."""
        try:
            return super().get_object()
        except Job.DoesNotExist:
            return None  # Return None to trigger creation logic in the update method

    def create(self, request, *args, **kwargs):
        """Handle creating a new job."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """Handle both update and create logic in the update method."""
        instance = self.get_object()
        if instance is None:
            # No existing instance, proceed with creation
            return self.create(request, *args, **kwargs)

        # If instance exists, proceed with update
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If prefetch cache exists, we need to invalidate it
            instance._prefetched_objects_cache = {}

        return Response(serializer.data, status=status.HTTP_200_OK)
    
  
class JobAcceptionCreateView(generics.CreateAPIView):
    queryset = JobAcception.objects.all()
    serializer_class = JobAcceptionSerializer
    permission_classes = [IsAuthenticated, IsProfessionalUser]  # Ensure only authenticated professionals can accept jobs

    def perform_create(self, serializer):
        # Here you can also check if the current user is allowed to accept the job (optional)
        # e.g., if self.request.user is a professional, then allow
        serializer.save()




class JobCompleteUpdateView(generics.UpdateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobCompletionSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can update

    def update(self, request, *args, **kwargs):
        job = self.get_object()
        serializer = self.get_serializer(job, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    
class AvailableJobListView(generics.ListAPIView):
    """
    List all available jobs (where is_avialable = True).
    """
    queryset = Job.objects.filter(is_avialable=True)
    serializer_class = JobSerializer
    permission_classes = [AllowAny]  # Anyone can view the available jobs