from uuid import uuid4
from django.db import models
from django.contrib.postgres.fields import ArrayField
from organizations.models import Organization
from users.models import UserProfile


def generate_guid():
    return uuid4().hex


class Project(models.Model):
    project_status = (('active', 'Active'), ('inactive', 'Inactive'), ('archived', 'Archived'))

    id = models.CharField(primary_key=True, max_length=32, default=generate_guid)
    name = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    # logo = models.ImageField(upload_to=ModelHelper.get_upload_path_thumb, editable=False, default=None, null=True, blank=True)
    logo = models.CharField(max_length=256, null=True, blank=True)
    status = models.CharField(max_length=8, choices=project_status, default='active')
    organization = models.ForeignKey(to=Organization, on_delete=models.CASCADE, null=True, blank=True)
    manager = models.ForeignKey(to=UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    member_ids = ArrayField(base_field=models.CharField(max_length=32), default=[])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "projects"
