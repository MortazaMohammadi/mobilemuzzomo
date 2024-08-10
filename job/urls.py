from django.urls import path
from .views import JobListView, JobDetailView , CompletedJobView , ProfessionalJobListView , ProfessionalCompletedJobListView
urlpatterns = [
  path('jobs-list/' , JobListView.as_view() , name = 'jobs-list'),
  path('job-detail/<int:pk>/' , JobDetailView.as_view() , name="job-detail"),
  path('completed-job/' , CompletedJobView.as_view() , name="completed-job"),
  path('professional-jobs/<int:user_id>/' ,ProfessionalJobListView.as_view() , name="professional-jobs"),
  path('professional-completed-jobs/<int:user_id>/' ,ProfessionalCompletedJobListView.as_view() , name="professional-completed-jobs"),
]