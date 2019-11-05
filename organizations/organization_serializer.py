from rest_framework import serializers
from organizations.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name', 'slug', 'logo', 'status', 'admin_json', 'member_ids', 'created_at', 'updated_at')
