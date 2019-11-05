from rest_framework import serializers
from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'attachments', 'status', 'deadline', 'project_json', 'created_by_json',
                  'assignee_json', 'assigned_json', 'task_type', 'details', 'created_at', 'updated_at')
