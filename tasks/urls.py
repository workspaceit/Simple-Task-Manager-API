from django.urls import path
from rest_framework.routers import SimpleRouter
from tasks.views import TaskViewSet


router = SimpleRouter()
router.register('', TaskViewSet)
