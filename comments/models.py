from uuid import uuid4

from django.db import models
from rest_framework.fields import JSONField

from django.contrib.postgres.fields.jsonb import JSONField as JSONBField



# Create your models here.93@#

def generate_guid():
    return uuid4().hex



class Comment(models.Model):
    id = models.CharField(primary_key=True, max_length=32, default=generate_guid)
    comment_to_json = JSONBField(null=True, blank=True)
    comment_description = models.TextField(null=True, blank=True)
    created_by_json = JSONBField(null=True, blank=True)
    task_to_json = JSONBField(null=True, blank=True)
    attachments = JSONBField(default=list, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name

    class Meta:
        db_table = "comments"
