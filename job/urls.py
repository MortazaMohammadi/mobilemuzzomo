from django.urls import path
from .views import JobAcceptionCreateView, JobCompleteUpdateView, JobCreateUpdateView, JobListView, JobDetailView , CompletedJobView , ProfessionalJobListView , ProfessionalCompletedJobListView
urlpatterns = [
  path('jobs-list/' , JobListView.as_view() , name = 'jobs-list'),
  path('job-detail/<int:pk>/' , JobDetailView.as_view() , name="job-detail"),
  path('completed-job/' , CompletedJobView.as_view() , name="completed-job"),
  path('professional-jobs/<int:user_id>/' ,ProfessionalJobListView.as_view() , name="professional-jobs"),
  path('professional-completed-jobs/<int:user_id>/' ,ProfessionalCompletedJobListView.as_view() , name="professional-completed-jobs"),



  # URL for creating a job (no primary key needed)
  path('job/create/', JobCreateUpdateView.as_view(), name='job-create'),
    
    # URL for retrieving or updating an existing job (with primary key)
  path('job/update/<int:pk>/', JobCreateUpdateView.as_view(), name='job-update'),

  path('job-accept/', JobAcceptionCreateView.as_view(), name='job-accept'),

  # URL for updating a job's completion status
    path('job/complete/<int:pk>/', JobCompleteUpdateView.as_view(), name='job-complete'),
]