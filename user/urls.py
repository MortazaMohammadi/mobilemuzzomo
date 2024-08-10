from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name = 'register'),
    path('verify/', VerifyUserEmail.as_view(), name = 'VerifyEmail'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('profile/', TestAuthenticationView.as_view(), name='granted'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='password-reset-confirm'),
    path('set-new-password/', SetNewPassword.as_view(), name='set-new-password'),
    path('user-profile-image/', UserProfileImageView.as_view(), name='user-profile-image'),
    path('user-addresses/', UserAddressListCreateView.as_view(), name='user-addresses-list-create'),
    path('user-addresses/<int:pk>/', UserAddressDeleteView.as_view(), name='user-addresses-delete'),
    path('update-email/', UserEmailUpdateView.as_view(), name='update-email'),
    path('verify-email-update/', UserEmailVerifyUpdateView.as_view(), name='verify-email'),
    path('update-password/', UpdatePasswordView.as_view(), name='update-password'),
    path('professional/', ProfessionalListCreateView.as_view(), name='professional-list-create'),
    path('professional-detial/', ProfessionalDetailView.as_view(), name='professional-detail'),
    path('professional-services/', ProfessionalServiceListCreateView.as_view(), name='professional-service-list-create'),
    # path('professional-dashboard-detail/<int:pk>/' , ProfessionalDashboardDetailView.as_view() , name='professional-dashboard-detail'),
    # path('user-update/<int:pk>/' , CustomUserUpdateView.as_view() , name='user-update'),
    # path('professionals/<int:admin__pk>/update-address/', ProfessionalUpdateAddressView.as_view(), name='update-address'),
    # -------------------------------------- professional and provider -----------------------------
    # path('professionalView/<int:pk>/', ProfessionalView.as_view(), name='professionalView'),
    # -------------------------------------- professional and provider -----------------------------
    
   
]