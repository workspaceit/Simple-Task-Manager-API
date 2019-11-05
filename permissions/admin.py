from django.contrib import admin

# Register your models here.
from permissions.models import StmUserPermission, Role, PermissionT, UserRole, RolePermission


# @admin.register(StmUserPermission)
# class StmUserPermissionAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'organization', 'permission')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Role._meta.fields]


@admin.register(PermissionT)
class PermissionAdmin(admin.ModelAdmin):
    list_display = [f.name for f in PermissionT._meta.fields]


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = [f.name for f in UserRole._meta.fields]


@admin.register(RolePermission)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = [f.name for f in RolePermission._meta.fields]
