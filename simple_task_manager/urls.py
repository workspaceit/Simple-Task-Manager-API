"""simple_task_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from uploads.views import HelperView
from users.views import UserProfileView
from users.urls import router as user
from organizations.urls import router as org
from organizations.urls import org_custom_urls
from permissions.urls import router as permission
from projects.urls import router as project
from tasks.urls import router as task
from django.conf.urls import url
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('docs/', include_docs_urls(title='STM API Docs')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('api/upload/file-upload/', csrf_exempt(HelperView.file_upload), name="file-upload"),
    path('api/user-register/', csrf_exempt(UserProfileView.as_view()), name="user-register"),
    path('api/users/', include(user.urls)),
    path('api/organizations/', include(org.urls)),
    path('api/<org_slug>/projects/', include(project.urls)),
    path('api/<org_slug>/projects/<project_id>/tasks/', include(task.urls)),
    path('api/authorize/', include('permissions.urls')),

] + org_custom_urls
