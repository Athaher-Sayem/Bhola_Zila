from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, PreAdmin

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = ['name', 'email', 'student_id', 'role', 'is_email_verified', 'is_verified']
    list_filter = ['role', 'is_email_verified', 'is_verified']
    search_fields = ['name', 'email', 'student_id']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('name', 'student_id')}),
        ('Permissions', {'fields': ('role', 'is_email_verified', 'is_verified', 'is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'name', 'student_id', 'password1', 'password2')}),
    )
    ordering = ['email']

@admin.register(PreAdmin)
class PreAdminAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'designation']
