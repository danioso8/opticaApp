from django.contrib import admin
from .models import Category, Product, Sale, SaleItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'price', 'stock', 'needs_restock', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'sku']
    list_editable = ['price', 'stock']


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['sale_number', 'get_customer_display', 'sold_by', 'payment_method', 'total', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['sale_number', 'customer_name', 'patient__full_name']
    inlines = [SaleItemInline]
    readonly_fields = ['sale_number', 'subtotal', 'total', 'created_at', 'updated_at']
