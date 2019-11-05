from rest_framework import serializers
from permissions.models import PermissionT


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionT
        fields = '__all__'
