import os
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated


class HelperPermission(permissions.BasePermission):
    """ Checking user's action permission"""

    def has_permission(self, request, view):
        # uid = request.user.userprofile.uid
        if request.user.is_superuser:
            return True
        if request.method == 'POST':
            return True


class HelperView(APIView):
    permission_classes = (IsAuthenticated, HelperPermission,)

    @api_view(('POST',))
    def file_upload(request, format=None):
        # upload image in temporary folder
        file = request.FILES['file']
        today = datetime.now()
        file_data = str(file.name).rsplit('.', 1)
        name = file_data[0] + "_" + str(int(today.strftime("%s"))) + '.' + file_data[1]
        filepath = os.path.join(
            'uploads/files/temp_files', name
        )
        with open(filepath, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return Response({"filepath": filepath}, status=status.HTTP_201_CREATED)
