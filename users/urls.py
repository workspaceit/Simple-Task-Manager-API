from django.urls import path
from rest_framework.routers import SimpleRouter
from users.views import UserProfileViewSet


router = SimpleRouter()
router.register('', UserProfileViewSet)
