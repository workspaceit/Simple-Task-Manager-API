import os
from tasks.task_serializer import TaskSerializer
from rest_framework import viewsets, status, serializers
from rest_framework.views import APIView
from tasks.models import Task
from organizations.models import Organization
from projects.models import Project
from users.models import UserProfile
from django.contrib.auth.models import Permission
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from shutil import copyfile
from rest_framework.pagination import PageNumberPagination
import magic
from rest_framework.decorators import api_view, action


class TaskPermission(permissions.BasePermission):
    """ Checking user's project action permission"""

    def has_permission(self, request, view):
        uid = request.user.userprofile.uid
        org_slug = request.parser_context.get('kwargs', {}).get('org_slug')
        project_id = request.parser_context.get('kwargs', {}).get('project_id')
        task_id = request.parser_context.get('kwargs', {}).get('pk')
        project = Project.objects.get(id=project_id)
        if project.organization.slug == org_slug:
            if task_id:
                if not Task.objects.filter(id=task_id, project_json__id=project_id).exists():
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


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated, TaskPermission,)
    pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        project_id = request.parser_context.get('kwargs', {}).get('project_id')
        queryset = self.filter_queryset(self.get_queryset()).filter(project_json__id=project_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            project_id = request.parser_context.get('kwargs', {}).get('project_id')
            project = Project.objects.get(id=project_id)
            # Task title should unique within a Project
            if not Task.objects.filter(title=request.data['title'], project_json__id=project_id).exists():
                request.POST._mutable = True
                request.data['project_json'] = {'id': project_id, 'name': project.name}
                user_name = request.user.first_name + " " + request.user.last_name
                request.data['created_by_json'] = {'uid': request.user.userprofile.uid, 'name': user_name,
                                                   'email': request.user.email}
                request.POST._mutable = False
            else:
                raise serializers.ValidationError({'title': 'Task title is exists in this project'})
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
        project_id = request.parser_context.get('kwargs', {}).get('project_id')
        # task title should unique within a project
        if 'title' in request.data:
            if Task.objects.filter(title=request.data['title'], project_json__id=project_id).exclude(
                    id=instance.id).exists():
                raise serializers.ValidationError({'title': 'Task title is exists in this project'})
        if 'assigned_user' in request.data:
            request.POST._mutable = True
            project = Project.objects.get(id=project_id)
            assigned_member_info = UserProfile.objects.filter(uid=request.data['assigned_user'],
                                                              organization_ids__contains=[project.organization.id])
            if assigned_member_info.exists():
                assigned_member = assigned_member_info[0]
                request.data['assigned_json'] = {'uid': assigned_member.uid,
                                                 'name': assigned_member.user.first_name + " " +
                                                         assigned_member.user.last_name,
                                                 'email': assigned_member.user.email}
                user_name = request.user.first_name + " " + request.user.last_name
                request.data['assignee_json'] = {'uid': request.user.userprofile.uid, 'name': user_name,
                                                 'email': request.user.email}
                request.POST._mutable = False
            else:
                raise serializers.ValidationError({'assigned_user': 'The member is not from this organization'})
        if 'attachments' in request.data:
            attachments_src = request.data['attachments']
            if instance.attachments:
                new_attachments = []
                for attachment_src in attachments_src:
                    mime = magic.Magic(mime=True)
                    mime_type = mime.from_file(attachment_src)
                    attachment_ext = str(attachment_src).rsplit('.', 1)[1]
                    user_name = request.user.first_name + " " + request.user.last_name
                    uploaded_by_json = {'uid': request.user.userprofile.uid, 'name': user_name,
                                        'email': request.user.email}
                    dst = attachment_src.split('/temp_files/')
                    attachment_dst = dst[0] + "/tasks/" + dst[1]
                    # copy new attachment from temp folder to Task folder
                    copyfile(attachment_src, attachment_dst)
                    # If temp file exists, delete it ##
                    if os.path.isfile(attachment_src):
                        os.remove(attachment_src)
                    attachment_json = {'path': attachment_dst, 'type': mime_type, 'extension': attachment_ext,
                                       'uploaded_by': uploaded_by_json}
                    new_attachments.append(attachment_json)
                all_attachments = instance.attachments + new_attachments
            else:
                all_attachments = []
                for attachment_src in attachments_src:
                    mime = magic.Magic(mime=True)
                    mime_type = mime.from_file(attachment_src)
                    attachment_ext = str(attachment_src).rsplit('.', 1)[1]
                    user_name = request.user.first_name + " " + request.user.last_name
                    uploaded_by_json = {"uid": request.user.userprofile.uid, "name": user_name,
                                        "email": request.user.email}
                    dst = attachment_src.split('/temp_files/')
                    attachment_dst = dst[0] + "/tasks/" + dst[1]
                    # copy new attachment from temp folder to Task folder
                    copyfile(attachment_src, attachment_dst)
                    # If temp file exists, delete it ##
                    if os.path.isfile(attachment_src):
                        os.remove(attachment_src)
                    attachment_json = {"path": attachment_dst, "type": mime_type, "extension": attachment_ext,
                                       "uploaded_by":
                                           uploaded_by_json}
                    all_attachments.append(attachment_json)
            request.POST._mutable = True
            request.data['attachments'] = all_attachments
            request.POST._mutable = False
        # remove attachment from array
        if 'remove_attachment' in request.data:
            request.POST._mutable = True
            attachment = request.data['remove_attachment']
            data = instance.attachments
            for element in data:
                if element['path'] == attachment:
                    # remove file from storage
                    if os.path.isfile(attachment):
                        os.remove(attachment)
                    index = data.index(element)
                    data.pop(index)
            request.data['attachments'] = data
            request.POST._mutable = False
        # remove assigned user
        if 'remove_user' in request.data:
            if instance.assigned_json and request.data['remove_user'] == instance.assigned_json['uid']:
                request.POST._mutable = True
                request.data['assigned_json'] = {}
                request.POST._mutable = False
            else:
                raise serializers.ValidationError({"remove_user": "Member is invalid"})
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
        # remove existing attachments
        if instance.attachments:
            for attachment in instance.attachments:
                if os.path.isfile(attachment['path']):
                    os.remove(attachment['path'])
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
