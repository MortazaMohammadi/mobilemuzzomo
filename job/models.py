from django.db import models
from service.models import *
from user.models import *
# Create your models here.
class Job(models.Model):
    submit_date = models.DateField(auto_now_add = True)
    start_date = models.DateTimeField(null = True, blank = True)
    complete_date = models.DateTimeField(null = True, blank = True)
    flexable = models.BooleanField(default = False)
    is_avialable = models.BooleanField(default = False)
    is_active = models.BooleanField(default =False)
    is_completed = models.BooleanField(default = False)
    address = models.ForeignKey(Address, on_delete = models.CASCADE)
    provider = models.ForeignKey(User, on_delete = models.CASCADE)
    service = models.ForeignKey(Service, on_delete = models.CASCADE)
    def __str__(self):
        return str(self.service)+' by '+str(self.pro)+' for '+ str(self.provider)
    
class JobAcception(models.Model):
    professional = models.ForeignKey(Professional, on_delete = models.CASCADE)
    Job = models.OneToOneField(Job, on_delete = models.CASCADE)