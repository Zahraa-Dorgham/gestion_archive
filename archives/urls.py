# archives/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'roles', views.RoleViewSet)
router.register(r'batiments', views.BatimentViewSet)
router.register(r'salles', views.SalleViewSet)
router.register(r'armoires', views.ArmoireViewSet)
router.register(r'etageres', views.EtagereViewSet)
router.register(r'phases-archive', views.PhaseArchiveViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('archives.auth_urls')),  # Routes d'authentification
]