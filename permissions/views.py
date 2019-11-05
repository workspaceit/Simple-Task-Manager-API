from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.db import connection

from permissions.models import PermissionT, Role, UserRole, RolePermission
from permissions.serializers import PermissionSerializer
from permissions.services import *
from simple_task_manager.models import PermissionConstant


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = PermissionT.objects.all()
    serializer_class = PermissionSerializer


@api_view(['POST', ])
def get_permissions(request):
    organization_id = request.data.get('organization_id', None)
    uid = request.user.userprofile.uid

    return Response(
        {
            "status": True,
            "message": "successfully sent",
            "permissions": get_permissoins_by_userid_orgid(uid=uid, organization_id=organization_id)

        })


@api_view(['POST', ])
def create_permission(request):
    title = request.data.get('title', None)
    description = request.data.get('description', None)
    user = request.user
    print(title)

    if is_parmitted_by_permission_title(title=PermissionConstant.CAN_CREATE_PERMISSION, user=user):
        PermissionT.objects.create(title=title, description=description, status=True)
        status = True
        message = "successfully permission created."

    else:
        status = False
        message = "you don't have permission to create any permission."

    return Response(
        {"status": status,
         "message": message,
         })


@api_view(['post', ])
def delete_permission(request):
    '''this is just demo function. modifie when need'''
    permission_id = request.data.get("permission_id", None)
    user = request.user

    if is_parmitted_by_permission_id(id=permission_id, user=user):
        # PermissionT.objects.create(title=title, description=description, status=True)
        status = True
        message = "successfully permission created."

    else:
        status = False
        message = "you don't have permission to create any permission."

    return Response(
        {"status": status,
         "message": message,
         })


@api_view(['POST', ])
def create_role(request):
    print(request.data)
    role_name = request.data.get("role_name", None)
    print("role name : " + role_name)
    organization_id = request.data.get('organization_id', None)
    print("organization id :" + organization_id)
    project_id = request.data.get('project_id')
    print("project id : " + project_id)
    '''check is role exist'''
    if len(Role.objects.filter(name=role_name, organization__id=organization_id, project_id=project_id)) > 0:
        return Response(
            {"status": False,
             "message": "This role already exist.",
             })

    '''check is user member of the organization and the project'''
    if is_user_member_of_organization_and_project_and_permission(organization_id=organization_id,
                                                                 user=request.user.userprofile,
                                                                 project_id=project_id,
                                                                 title=PermissionConstant.CAN_CREATE_ROLE):
        print("user is a member of the organization and project and has permission to create role.")
        '''creating role'''
        role = Role.objects.create(name=role_name, project_id=project_id, organization_id=organization_id, status=True)
        '''assigning role to user'''
        UserRole.objects.create(user=request.user.userprofile, role=role, status=True)
        message = "successfully created role and assigned to you."
        status = True
    else:
        print("user is not a member of the organization or the project or has not permission to create role.")
        status = False
        message = "you are not a member of the organization or the project or has not permission to create role."

    return Response(
        {"status": status,
         "message": message,
         })


@api_view(['POST', ])
def assign_role_to_user(request):
    ''' assigning role to user'''
    role_id = request.data.get("role_id", None)
    user_id = request.user.userprofile.uid
    try:
        role = Role.objects.get(id=role_id)
        try:
            user_role = UserRole.objects.get(role_id=role.id, user_id=user_id)
            user_role.status = True
            user_role.save()
            message = "successfully assigned"
            status = True
        except:
            UserRole.objects.create(role=role, user_id=user_id, status=True)
            message = "successfully assigned"
            status = True
    except:
        message = "not found"
        status = False
    return Response(
        {"status": status,
         "message": message,
         })


@api_view(['POST', ])
def revoke_role_from_user(request):
    ''' revoking role from user'''
    role_id = request.data.get("role_id", None)
    user_id = request.user.userprofile.uid
    try:
        role = Role.objects.get(id=role_id)
        try:
            user_role = UserRole.objects.get(role_id=role.id, user_id=user_id)
            user_role.status = False
            user_role.save()
            message = "successfully revoked"
            status = True
        except:
            message = "not found"
            status = False
    except:
        message = "not found"
        status = False
    return Response(
        {"status": status,
         "message": message,
         })


@api_view(['POST'])
def revoke_permission_from_role(request):
    '''revoking permission from role'''
    role_id = request.data.get('role_id', 0)
    permission_id = request.data.get('permission_id', 0)
    organization_id = request.data.get('organization_id', None)
    project_id = request.data.get('project_id', None)

    if role_id == 0 or permission_id == 0 or organization_id.isspace() or project_id.isspace():
        return Response({
            "status": False,
            "message": "please ensure all param"
        })

    if is_user_authorize_for_revoking_permission_from_role(request.user.userprofile,
                                                           organization_id=organization_id,
                                                           title=PermissionConstant.CAN_REVOKE_PERMISSION_FROM_ROLE):
        print("has authorization")
        try:
            instance = RolePermission.objects.get(role_id=role_id, permission_id=permission_id, )
            instance.status = False
            instance.save()
            status = True
            message = "has authorization. revoked permission."
        except:
            status = False
            message = "is is not assigned yet"
    else:
        status = False
        message = "has not authorization. not revoked permission"
    return Response(
        {"status": status,
         "message": message,
         })


@api_view(['POST'])
def assing_permission_to_role(request):
    '''revoking permission from role'''
    role_id = request.data.get('role_id', 0)
    permission_id = request.data.get('permission_id', 0)
    organization_id = request.data.get('organization_id', None)
    project_id = request.data.get('project_id', None)

    if role_id == 0 or permission_id == 0 or organization_id.isspace() or project_id.isspace():
        return Response({
            "status": False,
            "message": "please ensure all param"
        })

    if is_user_authorize_for_assigning_permission_to_role(user=request.user.userprofile,
                                                          organization_id=organization_id,
                                                          title=PermissionConstant.CAN_ASSIGN_PERMISSION_TO_ROLE):
        print("has authorization")
        try:
            instance = RolePermission.objects.get(role_id=role_id, permission_id=permission_id)
            instance.status = True
            instance.save()
            status = True
            message = "has authorization. assigned permission."
        except:
            RolePermission.objects.create(role_id=role_id, permission_id=permission_id, status=True)
            status = True
            message = "has authorization. assigned permission."
    else:
        status = False
        message = "has not authorization. not assigned permission"

    return Response(
        {"status": status,
         "message": message,
         })
