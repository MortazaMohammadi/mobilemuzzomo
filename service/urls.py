from django.contrib import admin
from django.urls import path

from .views import *

urlpatterns = [
    path('service-search/' , ServiceSearchListView.as_view() , name='service-search'),
    path('three-most-visited-services/' , ThreeMostVisitedServicesListView.as_view() , name='three-most-visited-services'),
    path('service/' , ServiceListView.as_view() , name="service"),
    path('service-catagory/' , ServiceCatagoryListView.as_view() , name="service-catagory"),
    path('service-detail/<int:pk>/' , ServiceDetailView.as_view() , name="service-detail"),
]