from django.contrib import admin
from django.urls import reverse
from django.db.models import Count
from django.contrib import messages
from django.utils.html import format_html
from django.utils.http import urlencode

from . import models


class InventoryListFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low'),
            ('>10', 'OK')
        ]

    def queryset(self, request, queryset):
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)
        elif self.value() == ">10":
            return queryset.filter(inventory__gt=10)


@admin.register(models.Products)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    prepopulated_fields = {
        'slug': ['title']
    }
    actions = ['clear_inventory']
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    list_editable = ['unit_price']
    list_select_related = ['collection']
    search_fields = ['title__istartswith']
    list_filter = ['collection', 'last_update', InventoryListFilter]

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'OK'

    @staticmethod
    def collection_title(product):
        return product.collection.title

    @admin.action(description='Clear Products')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} were updated successfully',
            messages.ERROR
        )


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    search_fields = ['title']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        return collection.products_count

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count('products'))


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership_choices']
    list_editable = ['membership_choices']
    search_fields = ['first_name']


class OrderItemInLine(admin.TabularInline):
    autocomplete_fields = ['products']
    model = models.OrderItem
    extra = 0
    min_num = 1
    max_num = 10


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    readonly_fields = ['placed_at']
    list_display = ['id', 'customer_first_name']
    list_select_related = ['customer']
    list_per_page = 10
    inlines = [OrderItemInLine]

    @admin.display(ordering='customer')
    def customer_first_name(self, order):
        url = (reverse("admin:store_customer_changelist") + '?' + urlencode({
            'id': order.customer.id
        }))
        return format_html("<a href={}>{}</a", url, order.customer.first_name)
