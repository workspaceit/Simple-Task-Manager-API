from django.contrib import admin
from organizations.models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    fields = ('name', 'slug', 'admin_json',)
    list_display = [f.name for f in Organization._meta.fields]

