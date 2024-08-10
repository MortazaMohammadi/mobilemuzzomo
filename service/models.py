from django.db import models

class ServiceCatagory(models.Model):
    title = models.CharField(max_length=50)
    photo = models.FileField(upload_to='serviceCatagroy', null=True)
    description = models.TextField()
    def __str__(self):
        return str(self.title)

class Service(models.Model):
    title = models.CharField(max_length=50)
    photo = models.FileField(upload_to='serviceType', null=True)
    description = models.TextField()
    catagory = models.ForeignKey(ServiceCatagory, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.catagory.title) +', '+ str(self.title)
