import os
from django.contrib.auth.models import Permission
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from shutil import copyfile
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, status, serializers
from projects.project_serializer import ProjectSerializer
from projects.models import Project
from organizations.models import Organization
from users.models import UserProfile


class ProjectPermission(permissions.BasePermission):
    """ Checking user's project action permission"""

    def has_permission(self, request, view):
        uid = request.user.userprofile.uid
        org_slug = request.parser_context.get('kwargs', {}).get('org_slug')
        project_id = request.parser_context.get('kwargs', {}).get('pk')
        if project_id:
            if not Project.objects.filter(id=project_id, organization__slug=org_slug).exists():
                return False
        if request.user.is_superuser:
            return True
        if request.method == 'POST':
            if Organization.objects.filter(admin_json__uid=uid).exists():
                return True
        elif request.method == 'GET':
            return True
        elif request.method in ['PUT', 'PATCH']:
            return True
        elif request.method == 'DELETE':
            return True
        return False


# Override default pagination settings
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated, ProjectPermission,)
    pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        # queryset = self.filter_queryset(self.get_queryset())
        org_slug = request.parser_context.get('kwargs', {}).get('org_slug')
        queryset = Project.objects.filter(organization__slug=org_slug)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            org_slug = request.parser_context.get('kwargs', {}).get('org_slug')
            organization = Organization.objects.get(slug=org_slug)
            # project name should unique within a organization
            if not Project.objects.filter(name=request.data['name'], organization__id=organization.id).exists():
                request.POST._mutable = True
                if 'logo' in request.data:
                    logo_src = request.data['logo']
                    dst = logo_src.split('/temp_files/')
                    logo_dst = dst[0] + "/projects/" + dst[1]
                    # copy new logo from temp folder to project folder
                    copyfile(logo_src, logo_dst)
                    # If temp file exists, delete it ##
                    if os.path.isfile(logo_src):
                        os.remove(logo_src)
                    request.data['logo'] = logo_dst
                request.data['organization'] = organization.id
                request.POST._mutable = False
            else:
                raise serializers.ValidationError({'name': 'Project name is exists in this organization'})
        except Exception as e:
            print(e)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        try:
            # Add project permission
            edit_permission = Permission.objects.get(codename='change_project')
            delete_permission = Permission.objects.get(codename='delete_project')
            # End project permission
        except Exception as e:
            print(e)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        # project name should unique within a organization
        if 'name' in request.data:
            if Project.objects.filter(name=request.data['name'], organization__id=instance.organization.id).exclude(
                    id=instance.id).exists():
                raise serializers.ValidationError({'name': 'Project name is exists in this organization'})
        if 'logo' in request.data:
            logo_src = request.data['logo']
            if logo_src:
                # remove existing logo
                if instance.logo:
                    if os.path.isfile(instance.logo):
                        os.remove(instance.logo)
                dst = logo_src.split('/temp_files/')
                logo_dst = dst[0] + "/projects/" + dst[1]
                # copy new logo from temp folder to project folder
                copyfile(logo_src, logo_dst)
                # If temp file exists, delete it ##
                if os.path.isfile(logo_src):
                    os.remove(logo_src)
                request.POST._mutable = True
                request.data['logo'] = logo_dst
                request.POST._mutable = False
        # Add or update user to project
        if 'member_ids' in request.data:
            if instance.member_ids:
                if UserProfile.objects.filter(organization_ids__contains=[instance.organization.id],
                                              uid__in=request.data['member_ids']).count() == len(
                        request.data['member_ids']):
                    all_members = list(set().union(instance.member_ids, request.data['member_ids']))
                    request.POST._mutable = True
                    request.data['member_ids'] = all_members
                    request.POST._mutable = False
                else:
                    raise serializers.ValidationError({'member_ids': 'Member do not have permission in this project'})
        # Remove user from project
        if 'remove_users' in request.data:
            request.POST._mutable = True
            request.data['member_ids'] = list(set(instance.member_ids).difference(set(request.data['remove_users'])))
            request.POST._mutable = False
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # remove existing logo
        if instance.logo:
            if os.path.isfile(instance.logo):
                os.remove(instance.logo)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
