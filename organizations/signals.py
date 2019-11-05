from django.db.models.signals import post_save
from django.dispatch import receiver

from organizations.models import Organization
from permissions.models import Role, UserRole, RolePermission, PermissionT

'''
When organization is created user gets admin role of the organization.
so here create a role name Admin with related to the created organization 
'''


@receiver(post_save, sender=Organization)
def create_organization(sender, created=False, instance=None, **kwargs):
    import inspect
    uid = ""
    request = None
    org_id = instance.id
    role = None
    for frame_record in inspect.stack():
        if frame_record[3] == 'get_response':
            request = frame_record[0].f_locals['request']
            uid = request.user.userprofile.uid

    if created and uid != "":
        role = Role.objects.create(name="Owner", organization=instance, status=True)
        UserRole.objects.create(user=request.user.userprofile, role=role, status=True)

        for permission in PermissionT.objects.all():
            RolePermission.objects.create(permission=permission, role=role, status=True)
