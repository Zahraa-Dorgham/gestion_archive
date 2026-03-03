# archives/auth_urls.py
from django.urls import path
from . import auth_views

# IMPORTANT: Ne pas répéter 'auth/' ici car déjà dans urls.py
urlpatterns = [
    path('register/', auth_views.RegisterView.as_view(), name='register'),
    path('login/', auth_views.CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh/', auth_views.TokenRefreshView.as_view(), name='refresh'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', auth_views.UserProfileView.as_view(), name='profile'),
    path('change-password/', auth_views.ChangePasswordView.as_view(), name='change-password'),
]