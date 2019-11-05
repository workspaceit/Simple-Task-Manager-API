from rest_framework import viewsets, status, serializers
from django.contrib.auth.models import Permission
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from organizations.organization_serializer import OrganizationSerializer
from organizations.models import Organization
from projects.models import Project
from tasks.models import Task
from users.models import UserProfile
from permissions.models import StmUserPermission
import json
from django.shortcuts import HttpResponse
from django.db.models import Q
from oauth2_provider.models import AccessToken
from rest_framework.decorators import api_view, permission_classes as pp_c
from django.contrib.auth.models import User as AuthUser
from users.user_serializer import UserProfileSerializer
from django.core.validators import validate_email

class OrganizationPermission(permissions.BasePermission):
    """ Checking user's organization action permission"""

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'POST' or request.method == 'GET':
            return True
        # elif request.method == 'GET':
        #     # print(request.user)
        #     org_id = request.parser_context.get('kwargs', {}).get('pk')
        #     # org_id = None, when request is to get all organizations, (which need su permissions)
        #     # need to check user's organization's permission
        #     if org_id and StmUserPermission.objects.filter(user_id=request.user.userprofile.uid, organization_id=org_id,
        #                                                    permission__codename='change_organization').exists():
        #         return True
        # return True
        elif request.method in ['PUT', 'PATCH']:
            org_id = request.parser_context.get('kwargs', {}).get('pk')
            if StmUserPermission.objects.filter(user_id=request.user.userprofile.uid, organization_id=org_id,
                                                permission__codename='change_organization').exists():
                return True
        elif request.method == 'DELETE':
            org_id = request.parser_context.get('kwargs', {}).get('pk')
            if StmUserPermission.objects.filter(user_id=request.user.userprofile.uid, organization_id=org_id,
                                                permission__codename='delete_organization').exists():
                return True
        return False


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = (IsAuthenticated, OrganizationPermission,)

    def list(self, request, *args, **kwargs):
        if request.user.is_superuser:
            queryset = self.filter_queryset(self.get_queryset())
        else:
            q = Q()
            q = q | Q(admin_json__uid=request.user.userprofile.uid)
            q = q | Q(member_ids__contains=[request.user.userprofile.uid])
            queryset = Organization.objects.filter(q)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        uid = request.user.userprofile.uid
        admin_json = dict(
            uid=uid,
            username=request.user.username,
            first_name=request.user.first_name,
        )
        request.POST._mutable = True
        request.data['admin_json'] = admin_json
        request.POST._mutable = False

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        try:
            org_id = serializer.data['id']
            # start adding permission
            edit_permission = Permission.objects.get(codename='change_organization')
            delete_permission = Permission.objects.get(codename='delete_organization')
            StmUserPermission(user_id=uid, permission_id=edit_permission.id,
                              organization_id=org_id).save()
            StmUserPermission(user_id=uid, permission_id=delete_permission.id,
                              organization_id=org_id).save()
            # end permission

            # set user_profile current_organization
            UserProfile.objects.filter(uid=uid).update(current_organization_id=org_id)
        except Exception as exception:
            print(exception)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        # Add or update user to organization
        if 'member_ids' in request.data:
            if instance.member_ids:
                member_list = UserProfile.objects.filter(uid__in=request.data['member_ids'])

                print(member_list.query)
                print(member_list)
                print(request.data['member_ids'])

                if member_list.exists():
                    all_members = list(set().union(instance.member_ids, request.data['member_ids']))
                    request.POST._mutable = True
                    request.data['member_ids'] = all_members
                    request.POST._mutable = False
                    for member in member_list:
                        if instance.id not in member.organization_ids:
                            member.organization_ids.append(instance.id)
                            member.save()
                else:
                    raise serializers.ValidationError({'member_ids': 'Something went wrong. please try again'})
            else:
                member_list = UserProfile.objects.filter(uid__in=request.data['member_ids'])
                for member in member_list:
                    if instance.id not in member.organization_ids:
                        member.organization_ids.append(instance.id)
                        member.save()
        # Remove user from Organization
        if 'remove_users' in request.data:
            request.POST._mutable = True
            request.data['member_ids'] = list(
                set(instance.member_ids).difference(set(request.data['remove_users'])))
            request.POST._mutable = False
            member_list = UserProfile.objects.filter(uid__in=request.data['remove_users'])
            for member in member_list:
                member.organization_ids = list(set(member.organization_ids).difference(set([instance.id])))
                member.save()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    def getOrganizationMembers(request, *args, **kwargs):
        import json
        from django.shortcuts import HttpResponse
        from django.core.serializers import serialize
        param_org_id = request.GET.get('org_id')
        print(param_org_id)
        # org_member_ids = Organization.objects.filter(id='67f15ca04b184609aec41920baeed693').values_list('member_ids')
        org_member_ids = Organization.objects.filter(id=param_org_id).values_list('member_ids')
        member_list = []
        if len(org_member_ids) > 0:

            org_member_ids = [list(item) for item in org_member_ids[0]]
            org_members = UserProfile.objects.filter(uid__in=org_member_ids[0])
            for member in org_members:
                member_list.append({
                    'name': member.user.get_full_name(),
                    'uid': member.uid
                })
        return HttpResponse(json.dumps(member_list), status=status.HTTP_200_OK, )

    def getMembersToOrganization(request, *args, **kwargs):
        param_org_id = request.GET.get('org_id', '')
        param_search_key = request.GET.get('search_key', '')
        q = Q()
        q = q | Q(user__username__icontains=param_search_key)
        q = q | Q(user__first_name__icontains=param_search_key)
        q = q | Q(user__last_name__icontains=param_search_key)
        q = q | Q(user__email__icontains=param_search_key)
        all_members_object = UserProfile.objects.filter(q).exclude(organization_ids__contains=[param_org_id])
        member_list = []
        for member in all_members_object:
            member_list.append({
                'name': member.user.get_full_name(),
                'uid': member.uid
            })
        return HttpResponse(json.dumps(member_list), status=status.HTTP_200_OK, )

    def getMembersForProjectManager(request, *args, **kwargs):
        param_org_id = request.GET.get('org_id', '')
        param_search_key = request.GET.get('search_key', '')
        q = Q()
        q = q | Q(user__username__icontains=param_search_key)
        q = q | Q(user__first_name__icontains=param_search_key)
        q = q | Q(user__last_name__icontains=param_search_key)
        q = q | Q(user__email__icontains=param_search_key)
        all_members_object = UserProfile.objects.filter(q).filter(organization_ids__contains=[param_org_id])
        member_list = []
        for member in all_members_object:
            member_list.append({
                'name': member.user.get_full_name(),
                'uid': member.uid
            })
        return HttpResponse(json.dumps(member_list), status=status.HTTP_200_OK, )

    @api_view(['post'])
    @pp_c((IsAuthenticated,))
    def switch_organization(request):
        user = {'uid': None, 'org_id': None, 'org_slug': None, 'org_name': None}
        response_status = status.HTTP_400_BAD_REQUEST
        org_id = json.loads(request.body).get('org_id', '').strip()
        if Organization.objects.filter(id=org_id).exists():
            try:
                user_profile = request.user.userprofile
                user_profile.current_organization_id = org_id
                user_profile.save()
                user['uid'] = user_profile.uid
                user['name'] = user_profile.user.get_full_name()
                if user_profile.current_organization:
                    user['org_id'] = user_profile.current_organization_id
                    user['org_slug'] = user_profile.current_organization.slug
                    user['org_name'] = user_profile.current_organization.name
                response_status = status.HTTP_200_OK
            except Exception as ex:
                print(ex)
        return Response(user, status=response_status, )

    def getUserInfo(request, *args, **kwargs):
        user = {'uid': None, 'org_id': None, 'org_slug': None, 'org_name': None}
        response_status = status.HTTP_400_BAD_REQUEST
        token = request.META.get('HTTP_AUTHORIZATION')
        if token:
            try:
                token = token.split(' ')[1]
                user_profile = AccessToken.objects.get(token=token).user.userprofile
                user['uid'] = user_profile.uid
                user['name'] = user_profile.user.get_full_name()
                if user_profile.current_organization:
                    user['org_id'] = user_profile.current_organization_id
                    user['org_slug'] = user_profile.current_organization.slug
                    user['org_name'] = user_profile.current_organization.name
                response_status = status.HTTP_200_OK
            except Exception as ex:
                print(ex)
        return HttpResponse(json.dumps(user), status=response_status, )

    @api_view(['post'])
    def verify_user_email(request):
        user = {'email': None, 'org_id': None, 'org_slug': None, 'org_name': None}
        response_status = status.HTTP_200_OK
        user_email = request.data.get('user_email', '').strip()
        user_data = []

        try:
            user_data = UserProfile.objects.get(user__email=user_email)
            user = UserProfileSerializer(user_data).data
            response_status = status.HTTP_200_OK
        except UserProfile.DoesNotExist:
            user = "User dose not not exists"
        except Exception as ex:
            response_status = status.HTTP_400_BAD_REQUEST
            error_message = "Something went wrong."

        return Response(user, status=response_status, )

    ##
    # Delete all Project under a certain Organization
    ##
    @api_view(['delete'])
    def delete_project_by_org_id(request, org_id):
        response_status = status.HTTP_200_OK
        token = request.META.get('HTTP_AUTHORIZATION')
        print(token)
        error_message = "Project successfully deleted."
        print(org_id)
        if token:
            try:
                project = Project.objects.filter(organization_id=org_id)
                print(project)
                if project:
                    for project_item in project:
                        project_item.delete()
                        print(project)
                        print("fdfdf")
                    response_status = status.HTTP_200_OK
                else:
                    error_message = "Project dose not not exists."
            except Project.exists():
                error_message = "Project dose not not exists."
            except Exception as ex:
                response_status = status.HTTP_400_BAD_REQUEST
                error_message = "Something went wrong."

        return Response(error_message, status=response_status, )

    ##
    # Delete All member under a specific Organization
    ##
    @api_view(['delete'])
    def delete_all_member_by_org_id(request, org_id):
        response_status = status.HTTP_200_OK
        token = request.META.get('HTTP_AUTHORIZATION')
        print(token)
        error_message = "Member successfully deleted."
        print(org_id)
        if token:
            try:
                organization = Organization.objects.get(pk=org_id)
                print(organization)
                if organization:
                    organization.member_ids = []
                    organization.save()
                    print(type(organization))
                    response_status = status.HTTP_200_OK
                    error_message = "Member successfully remove."
                else:
                    error_message = "Member dose not not exists."
            except Organization.DoesNotExist:
                error_message = "Organization dose not not exists."
                response_status = status.HTTP_200_OK
            except Exception as ex:
                response_status = status.HTTP_400_BAD_REQUEST
                error_message = "Something went wrong."

        return Response(error_message, status=response_status, )

    ##
    # Delete all task under a certain project
    ##
    @api_view(['delete'])
    def delete_project_by_project_id(request, project_id):
        response_status = status.HTTP_200_OK
        token = request.META.get('HTTP_AUTHORIZATION')
        error_message = "Project successfully remove."
        if token:
            try:
                # task = Task.objects.filter(project_json__id=[project_id])
                Project.objects.get(pk=project_id).delete()
                task = Task.objects.filter(project_json__contains={'id': project_id})
                print(task)
                if task:
                    for task_item in task:
                        print(task_item)
                        task_item.delete()
                    response_status = status.HTTP_200_OK
            except Project.DoesNotExist:
                response_status = status.HTTP_200_OK
                error_message = "Project does not exist."
            except Exception as ex:
                response_status = status.HTTP_400_BAD_REQUEST
                error_message = "Something went wrong."

        return Response(error_message, status=response_status, )

    ##
    # Delete all task under a certain Org
    ##
    @api_view(['delete'])
    def delete_org_by_org_id(request, org_id):
        response_status = status.HTTP_200_OK
        token = request.META.get('HTTP_AUTHORIZATION')
        error_message = "Organization successfully remove."
        if token:
            try:
                organization = Organization.objects.get(pk=org_id)
                try:
                    organization.delete()
                    project = Project.objects.filter(organization_id=org_id).only("id")
                    if project:
                        for project_item in project:
                            try:
                                # task = Task.objects.filter(project_json__id=[project_id])
                                task = Task.objects.filter(project_json__contains={'id': project_item.id})
                                project_item.delete()
                                if task:
                                    for task_item in task:
                                        task_item.delete()
                            except Task.DoesNotExist:
                                response_status = status.HTTP_400_BAD_REQUEST
                                error_message = "Something went wrong."
                            except Exception as ex:
                                response_status = status.HTTP_400_BAD_REQUEST
                                error_message = "Something went wrong."
                except Exception as ex:
                    response_status = status.HTTP_400_BAD_REQUEST
                    error_message = "Something went wrong."
            except Organization.DoesNotExist:
                response_status = status.HTTP_200_OK
                error_message = "Organization dose not not exists."
            except Exception as ex:
                response_status = status.HTTP_400_BAD_REQUEST
                error_message = "Something went wrong."
        return Response(error_message, status=response_status, )

    ##
    # This Method for email checking for register account
    ##

    @api_view(['post'])
    def has_account(request):

        response_status = status.HTTP_200_OK
        user_email = request.data.get('valid_email', '').strip()

        try:
            validate_email(user_email)
            try:
                UserProfile.objects.get(user__email=user_email)
                response_message = "You are all ready registered.Please log in your account."
                # response["response_flag"]=True
            except UserProfile.DoesNotExist:
                response_status = status.HTTP_201_CREATED
                response_message = "You are successfully register.Please check you mail."
            except Exception as ex:
                response_status = status.HTTP_400_BAD_REQUEST
                response_message = "Some thing went wrong!"
                # response["response_flag"] = False
        except Exception as ex:
            response_status = status.HTTP_400_BAD_REQUEST
            response_message = "Please register email valid address."

        return Response(response_message, status=response_status, )
