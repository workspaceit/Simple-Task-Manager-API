from django.db import models


class AbstractBaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PermissionConstant:
    CAN_ASSIGN_PERMISSION_TO_ROLE = 'can_assign_permission_to_role'
    CAN_REVOKE_PERMISSION_FROM_ROLE = 'can_revoke_permission_from_role'
    CAN_CREATE_PERMISSION = 'can_create_permission'
    CAN_CREATE_ROLE = 'can_create_role_for_organization_of_a_project'
    CAN_LOGIN = 'can_login'
    CAN_REGISTER = 'can_register'

