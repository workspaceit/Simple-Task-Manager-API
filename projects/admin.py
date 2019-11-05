from django.contrib import admin
from projects.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'manager',)
    list_display = [f.name for f in Project._meta.fields]