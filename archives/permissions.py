# archives/permissions.py
from rest_framework import permissions

class EstAdministrateur(permissions.BasePermission):
    """Permission pour les administrateurs"""
    message = "Vous devez être administrateur pour effectuer cette action."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.groups.filter(name='Administrateur').exists()
        )

class EstArchiviste(permissions.BasePermission):
    """Permission pour les archivistes"""
    message = "Vous devez être archiviste pour effectuer cette action."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.groups.filter(name='Archiviste').exists() or
            request.user.groups.filter(name='Administrateur').exists()
        )

class EstResponsable(permissions.BasePermission):
    """Permission pour les responsables de service"""
    message = "Vous devez être responsable pour effectuer cette action."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.groups.filter(name='Responsable').exists() or
            request.user.groups.filter(name='Archiviste').exists() or
            request.user.groups.filter(name='Administrateur').exists()
        )

class EstEmploye(permissions.BasePermission):
    """Permission pour les employés (lecture seule généralement)"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class PeutModifierDocument(permissions.BasePermission):
    """Permission basée sur l'objet (exemple pour les documents)"""
    
    def has_object_permission(self, request, view, obj):
        # Lecture autorisée pour tous les employés
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Modification autorisée seulement pour certains rôles
        user = request.user
        return (
            user.is_superuser or
            user.groups.filter(name='Administrateur').exists() or
            user.groups.filter(name='Archiviste').exists()
        )

class EstProprietaireOuArchive(permissions.BasePermission):
    """Permission pour les documents - seul le propriétaire ou archiviste peut modifier"""
    
    def has_object_permission(self, request, view, obj):
        # Lecture autorisée pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Vérifier si l'utilisateur est le propriétaire (si le document a un champ created_by)
        if hasattr(obj, 'created_by') and obj.created_by == request.user:
            return True
        
        # Vérifier les rôles autorisés
        return (
            request.user.is_superuser or
            request.user.groups.filter(name='Administrateur').exists() or
            request.user.groups.filter(name='Archiviste').exists()
        )