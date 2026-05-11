from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
# Register your models here.



@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ('email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
    list_filter   = ('role', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering      = ('-date_joined',)

    fieldsets = (
        (None,            {'fields': ('email', 'password')}),
        ('Informations',  {'fields': ('first_name', 'last_name', 'phone', 'photo')}),
        ('Rôle & accès',  {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Dates',         {'fields': ('last_login_date',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )