from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from store.models import Products
from tags.models import TagItem
from store.admin import ProductAdmin


class TagInLine(GenericTabularInline):
    model = TagItem
    autocomplete_fields = ['tag']


class CustomProductAdmin(ProductAdmin):
    inlines = [TagInLine]


admin.site.unregister(Products)
admin.site.register(Products, CustomProductAdmin)
