from django.contrib import admin
from .models import *


# class CustomUserinline(admin.TabularInline):
#     model = CustomUser
#     fields = ['username','first_name','last_name', 'Email','phone','address','is_active']
#     extra = 1
#     search_fields = ['username']
    


# @admin.register(Professional)
# class ProAdmin(admin.ModelAdmin):
#     list_display = ['id',  'license_no','insurance_number','service']
#     inlines = [CustomUserinline]

    
# # @admin.register(Service)
# class CustomUserAdmin(admin.ModelAdmin):
#     list_display = ['id', 'username', 'email', 'service','is_active']
#     list_filter = ['username']
#     search_fields = ['title']

admin.site.register(Country)
admin.site.register(Province)
admin.site.register(City)
admin.site.register(Address)
admin.site.register(User)
admin.site.register(Professional)
admin.site.register(OneTimePassword)
admin.site.register(UserAddress)
admin.site.register(EmailUpdateCode)
# Register your models here.