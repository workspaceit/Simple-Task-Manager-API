from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import UserProfile
from users.user_serializer import UserProfileSerializer
from rest_framework.permissions import BasePermission
from rest_framework import status


class UserProfilePermissions(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'POST':
            return True
        elif request.user.is_authenticated and request.method in ['GET', 'PUT', 'PATCH']:
            uid = request.parser_context.get('kwargs', {}).get('pk')
            if request.user.userprofile.uid == uid:
                return True
        return False


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (UserProfilePermissions,)


class UserProfileView(APIView):
    def post(self, request, format=None):
        serializer = UserProfileSerializer(data=request.data)
        print("----view-----")
        print(request.data)
        print("---------")
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
