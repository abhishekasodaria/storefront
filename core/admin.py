from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import User
from store.models import Products
from tags.models import TagItem
from store.admin import ProductAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "email", "first_name", "last_name"),
            },
        ),
    )

class TagInLine(GenericTabularInline):
    model = TagItem
    autocomplete_fields = ['tag']


class CustomProductAdmin(ProductAdmin):
    inlines = [TagInLine]


admin.site.unregister(Products)
admin.site.register(Products, CustomProductAdmin)
