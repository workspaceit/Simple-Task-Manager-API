from uuid import uuid4
from django.db import models
from django.contrib.auth.models import Permission
from organizations.models import Organization
from projects.models import Project
from simple_task_manager.models import AbstractBaseModel
from tasks.models import Task
from users.models import UserProfile


def generate_guid():
    return uuid4().hex


class StmUserPermission(models.Model):
    id = models.CharField(primary_key=True, max_length=32, default=generate_guid)
    user = models.ForeignKey(to=UserProfile, on_delete=models.CASCADE)
    permission = models.ForeignKey(to=Permission, on_delete=models.CASCADE)
    organization = models.ForeignKey(to=Organization, on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey(to=Task, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.permission.name

    class Meta:
        db_table = 'stm_user_permissions'


class Role(AbstractBaseModel):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(to=Organization, related_name="roles", on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE, null=True, blank=True)
    users = models.ManyToManyField(UserProfile,
                                   through='UserRole',
                                   related_name='roles',
                                   through_fields=('role', 'user'),
                                   editable=False, )

    status = models.BooleanField(default=False, verbose_name='Active / Inactive')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# A 'T' prefixed to avoid conflict with django.contrib.auth.models import Permission
# we can completely remove default role-based model as we are using here pure RBAC pattern
class PermissionT(AbstractBaseModel):
    title = models.CharField(max_length=100)
    status = models.BooleanField(default=False, verbose_name='Active / Inactive')
    roles = models.ManyToManyField(Role,
                                   through='RolePermission',
                                   related_name='permissions',
                                   through_fields=('permission', 'role'),
                                   editable=False, )
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Permission'

    def __str__(self):
        return self.title


class UserRole(AbstractBaseModel):
    user = models.ForeignKey(UserProfile, related_name='role_user', null=True, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, null=True, on_delete=models.CASCADE)
    status = models.BooleanField(default=False, verbose_name='Active / Inactive')
    description = models.TextField(blank=True, null=True)


class RolePermission(AbstractBaseModel):
    permission = models.ForeignKey(PermissionT, null=True, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, null=True, on_delete=models.CASCADE)
    status = models.BooleanField(default=False, verbose_name='Active / Inactive')
    description = models.TextField(blank=True, null=True)
