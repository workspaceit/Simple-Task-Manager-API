from rest_framework import serializers
from projects.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    manager_name = serializers.ReadOnlyField(source='manager.user.get_full_name')

    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'organization', 'manager', 'member_ids', 'logo', 'status', 'created_at',
                  'updated_at', 'manager_name')
