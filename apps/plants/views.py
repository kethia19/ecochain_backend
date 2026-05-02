"""
Plants views.
"""
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from .models import Plant, UserPlant
from .serializers import PlantSerializer, UserPlantSerializer


@extend_schema(tags=['Plants'])
class PlantDetailView(generics.RetrieveAPIView):
    """Public plant detail — looked up from a Green Match result."""
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


@extend_schema(tags=['Plants'])
class AddUserPlantView(generics.ListCreateAPIView):
    """List the user's garden, or add a new plant to it."""
    serializer_class = UserPlantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserPlant.objects.filter(user=self.request.user).select_related('plant')
