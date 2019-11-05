from uuid import uuid4
from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField


def generate_guid():
    return uuid4().hex


class Organization(models.Model):
    org_status = (('active', 'Active'), ('inactive', 'Inactive'))

    id = models.CharField(primary_key=True, max_length=32, default=generate_guid)
    email = models.EmailField(null=True, blank=True)
    name = models.CharField(max_length=128)
    slug = models.CharField(max_length=32, unique=True)
    description = models.TextField(null=True, blank=True)
    logo = models.CharField(max_length=256, null=True, blank=True)
    status = models.CharField(max_length=8, choices=org_status, default='active')
    admin_json = JSONField()
    member_ids = ArrayField(base_field=models.CharField(max_length=32), default=[])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "organizations"
