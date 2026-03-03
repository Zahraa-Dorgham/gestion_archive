# archives/auth_serializers.py
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Role

class UserSerializer(serializers.ModelSerializer):
    """Sérializer pour les utilisateurs"""
    roles = serializers.SerializerMethodField()
    groups = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'is_active', 'date_joined', 'groups', 'roles']
        read_only_fields = ['date_joined']

    def get_roles(self, obj):
        """Récupère les rôles personnalisés depuis les groupes"""
        return [group.name for group in obj.groups.all()]

class RegisterSerializer(serializers.ModelSerializer):
    """Sérializer pour l'inscription"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    role = serializers.CharField(write_only=True, required=False, help_text="Nom du rôle à assigner")

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 'first_name', 
                  'last_name', 'role']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs

    def create(self, validated_data):
        # Retirer les champs supplémentaires
        role_name = validated_data.pop('role', None)
        validated_data.pop('password2', None)
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        
        # Assigner un rôle si spécifié
        if role_name:
            try:
                # Vérifier d'abord dans les groupes Django
                group, created = Group.objects.get_or_create(name=role_name)
                user.groups.add(group)
                
                # Ou si vous utilisez votre modèle Role personnalisé
                try:
                    role = Role.objects.get(nom=role_name)
                    # Logique supplémentaire avec votre modèle Role
                except Role.DoesNotExist:
                    pass
                    
            except Exception as e:
                print(f"Erreur lors de l'assignation du rôle: {e}")
        
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Sérializer personnalisé pour le token JWT avec informations utilisateur"""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Ajouter des informations utilisateur au token
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'roles': [group.name for group in self.user.groups.all()],
            'is_staff': self.user.is_staff,
            'is_superuser': self.user.is_superuser,
        }
        
        return data

class ChangePasswordSerializer(serializers.Serializer):
    """Sérializer pour le changement de mot de passe"""
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password2 = serializers.CharField(required=True, style={'input_type': 'password'})

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Les mots de passe ne correspondent pas."})
        return attrs