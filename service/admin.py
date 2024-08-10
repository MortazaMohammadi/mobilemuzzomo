from django.contrib import admin
from .models import ServiceCatagory, Service

class ServiceCatagoryinline(admin.TabularInline):
    model = Service
    fields = ['title','description']
    extra = 1
    search_fields = ['title']
    


@admin.register(ServiceCatagory)
class ServiceCatagoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'photo', 'description']
    inlines = [ServiceCatagoryinline]

    
# @admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'photo', 'description', 'category']
    list_filter = ['category']
    search_fields = ['title']
    

admin.site.register(Service)