# archives/serializers.py - Version avec uniquement les modèles existants
from rest_framework import serializers
from .models import (
    Role, Batiment, Salle, Armoire, Etagere, PhaseArchive
    # Retirez Boitier, Dossier, Document, Service s'ils n'existent pas
)

# Serializer pour Role
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'nom', 'description', 'niveau']

# Serializer pour Batiment
class BatimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batiment
        fields = ['id', 'nom', 'code', 'adresse', 'description', 'date_creation']

# Serializer pour Salle
class SalleSerializer(serializers.ModelSerializer):
    batiment_nom = serializers.CharField(source='batiment.nom', read_only=True)
    
    class Meta:
        model = Salle
        fields = ['id', 'nom', 'code', 'batiment', 'batiment_nom', 'type_salle', 
                  'etage', 'description']

# Serializer pour Armoire
class ArmoireSerializer(serializers.ModelSerializer):
    salle_nom = serializers.CharField(source='salle.nom', read_only=True)
    
    class Meta:
        model = Armoire
        fields = ['id', 'code', 'type_armoire', 'salle', 'salle_nom', 
                   
                  'code_barres', 'description', 'date_installation']

# Serializer pour Etagere
class EtagereSerializer(serializers.ModelSerializer):
    armoire_code = serializers.CharField(source='armoire.code', read_only=True)
    
    class Meta:
        model = Etagere
        fields = ['id', 'armoire', 'armoire_code', 'numero', 'code_barres',
                  'capacite_max_boites', 'occupation_actuelle', 'description']

# Serializer pour PhaseArchive
class PhaseArchiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhaseArchive
        fields = ['id', 'nom', 'code', 'type_phase', 'duree_conservation',
                  'description', 'action_finale', 'ordre']