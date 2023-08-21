from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers

class RecipeViewSets(viewsets.ModelViewSet):
    """view for manage recipe APIs."""

    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrive recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')
    
    def get_serializer_class(self):
        """Returns the class that should be used for the serializer."""
        if self.action == 'list':
            return serializers.RecipeSerializers
        
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new user recipe."""
        serializer.save(user=self.request.user)

