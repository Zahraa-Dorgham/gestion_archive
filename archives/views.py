# archives/views.py - Version avec uniquement les modèles existants
from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Role, Batiment, Salle, Armoire, Etagere, PhaseArchive
from .serializers import (
    RoleSerializer, BatimentSerializer, SalleSerializer,
    ArmoireSerializer, EtagereSerializer, PhaseArchiveSerializer
)

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission: Lecture pour tous (authentifiés), écriture seulement pour admin
    """
    def has_permission(self, request, view):
        # Lecture autorisée pour tous les utilisateurs authentifiés
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Écriture réservée aux admins/staff
        return request.user and request.user.is_staff

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['nom', 'description']
    permission_classes = [IsAdminOrReadOnly]


class BatimentViewSet(viewsets.ModelViewSet):
    queryset = Batiment.objects.all()
    serializer_class = BatimentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['nom', 'code', 'adresse']
    permission_classes = [IsAdminOrReadOnly]


class SalleViewSet(viewsets.ModelViewSet):
    queryset = Salle.objects.all()
    serializer_class = SalleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['batiment', 'etage', 'climatisee']
    search_fields = ['nom', 'code']
    permission_classes = [IsAdminOrReadOnly]


class ArmoireViewSet(viewsets.ModelViewSet):
    queryset = Armoire.objects.all()
    serializer_class = ArmoireSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['salle', 'type_armoire']
    search_fields = ['code', 'code_barres']
    permission_classes = [IsAdminOrReadOnly]


class EtagereViewSet(viewsets.ModelViewSet):
    queryset = Etagere.objects.all()
    serializer_class = EtagereSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['armoire']
    search_fields = ['code_barres']
    permission_classes = [IsAdminOrReadOnly]


class PhaseArchiveViewSet(viewsets.ModelViewSet):
    queryset = PhaseArchive.objects.all()
    serializer_class = PhaseArchiveSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'code']
    ordering_fields = ['ordre', 'nom']
    permission_classes = [IsAdminOrReadOnly]