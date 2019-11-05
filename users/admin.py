from django.contrib import admin
from users.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    fields = ('user', 'phone_number', 'dob', 'current_organization')
    list_display = [f.name for f in UserProfile._meta.fields]
