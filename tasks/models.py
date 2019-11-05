from uuid import uuid4
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.fields.jsonb import JSONField as JSONBField


def generate_guid():
    return uuid4().hex


class Task(models.Model):
    task_status = (('open', 'Open'), ('closed', 'Closed'), ('disputed', 'Disputed'))
    task_types = (('task', 'Task'), ('meeting', 'Meeting'), ('call', 'Call'))

    id = models.CharField(primary_key=True, max_length=32, default=generate_guid)
    title = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    attachments = JSONBField(default=list, null=True, blank=True)
    status = models.CharField(max_length=8, choices=task_status, default='open')
    deadline = models.DateTimeField(null=True, blank=True)
    project_json = JSONField(null=True, blank=True)
    created_by_json = JSONField(null=True, blank=True)
    assignee_json = JSONField(null=True, blank=True)
    assigned_json = JSONField(null=True, blank=True)
    task_type = models.CharField(max_length=8, choices=task_types, default='task')
    details = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "tasks"
