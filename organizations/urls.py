from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import SimpleRouter

from organizations.views import OrganizationViewSet

router = SimpleRouter()
router.register('', OrganizationViewSet)

org_custom_urls = [
    path('api/organizations-members/', csrf_exempt(OrganizationViewSet.getOrganizationMembers)),
    path('api/all-members/', csrf_exempt(OrganizationViewSet.getMembersToOrganization)),
    path('api/all-members-for-project/', csrf_exempt(OrganizationViewSet.getMembersForProjectManager)),
    path('api/get-user-info/', csrf_exempt(OrganizationViewSet.getUserInfo)),
    path('api/switch-organization/', OrganizationViewSet.switch_organization),
    path('api/verify-email/', csrf_exempt(OrganizationViewSet.verify_user_email)),
    #path('api/<str:org_id>/delete-project/', csrf_exempt(OrganizationViewSet.delete_project_by_org_id)),
    path('api/<str:org_id>/delete-members/', csrf_exempt(OrganizationViewSet.delete_all_member_by_org_id)),
    path('api/<str:project_id>/delete-project/', csrf_exempt(OrganizationViewSet.delete_project_by_project_id)),
    path('api/<str:org_id>/delete-org/', csrf_exempt(OrganizationViewSet.delete_org_by_org_id)),
    path('api/user-account/', csrf_exempt(OrganizationViewSet.has_account)),
]
