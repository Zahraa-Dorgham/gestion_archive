# archives/auth_views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .auth_serializers import (
    UserSerializer, RegisterSerializer, 
    CustomTokenObtainPairSerializer, ChangePasswordSerializer
)

class RegisterView(generics.CreateAPIView):
    """Inscription d'un nouvel utilisateur"""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    """Login - obtenir token JWT avec infos utilisateur"""
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    """Déconnexion (blacklist token)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({'success': 'Déconnexion réussie'})
            return Response({'error': 'Token refresh requis'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """Profil de l'utilisateur connecté"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.UpdateAPIView):
    """Changement de mot de passe"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = self.get_object()
        
        # Vérifier l'ancien mot de passe
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': 'Mot de passe incorrect'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Changer le mot de passe
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'success': 'Mot de passe changé avec succès'})