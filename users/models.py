from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from organizations.models import Organization


def generate_guid():
    return uuid4().hex


class UserProfile(models.Model):
    uid = models.CharField(primary_key=True, max_length=32, default=generate_guid)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=32, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    organization_ids = ArrayField(base_field=models.CharField(max_length=32), default=[])
    project_ids = ArrayField(base_field=models.CharField(max_length=32), default=[])
    current_organization = models.ForeignKey(to=Organization, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    def delete(self, using=None, keep_parents=False):
        """ User deletion will delete UserProfile too """
        return self.user.delete()

    class Meta:
        db_table = "user_profiles"
