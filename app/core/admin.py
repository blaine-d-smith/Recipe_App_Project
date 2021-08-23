from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Tag, Ingredient, Recipe
from django.utils.translation import gettext as _


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name', 'last_login']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Personal'),
            {'fields': ('name',)}
        ),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (
            _('Dates'),
            {'fields': ('last_login',)}
        )
    )
    add_fieldsets = (
        (None,
         {'classes': ('wide',),
          'fields': ('email', 'password1', 'password2',)}
         ),
    )


# Register
admin.site.register(User, UserAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
