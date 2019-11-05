from django.urls import path
from django.conf.urls import url, include
from rest_framework.routers import SimpleRouter
from rest_framework import routers
from permissions import views

# router = SimpleRouter()
# router.register('', PermissionViewSet)

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'permissions', views.PermissionViewSet)

urlpatterns = [
    url(r'^get/permissions', views.get_permissions),
    url(r'^create/permission', views.create_permission),
    url(r'^delete/permission', views.delete_permission),
    url(r'^create/role', views.create_role),
    url(r'^assign/role', views.assign_role_to_user),  # assigning role to user
    url(r'^revoke/role', views.revoke_role_from_user),  # revoking role from user
    url(r'^assign/permission', views.assing_permission_to_role),  # assigning permission to role
    url(r'^revoke/permission', views.revoke_permission_from_role),  # revoking permission from role

    url(r'^', include(router.urls)),

]
