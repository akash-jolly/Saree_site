from django.contrib import admin
from .models import Category, Product, ProductVariant, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1  # how many empty variant rows to show by default


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "base_price", "active", "created_at")
    list_filter = ("active", "category")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "color", "blouse_option", "price", "stock")
    list_filter = ("blouse_option", "product__category")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("variant", "quantity", "price")
    can_delete = False  # prevents accidentally deleting order history


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "phone",
        "city",
        "total",
        "status",
        "payment_method",
        "payment_status",
        "created_at",
    )
    list_filter = ("status", "payment_method", "payment_status", "created_at", "city")
    search_fields = ("customer_name", "phone", "address_line1", "city", "pincode")
    inlines = [OrderItemInline]

    actions = [
        "mark_confirmed",
        "mark_packed",
        "mark_shipped",
        "mark_delivered",
        "mark_cancelled",
    ]

    @admin.action(description="Mark selected orders as Confirmed")
    def mark_confirmed(self, request, queryset):
        queryset.update(status="confirmed")

    @admin.action(description="Mark selected orders as Packed")
    def mark_packed(self, request, queryset):
        queryset.update(status="packed")

    @admin.action(description="Mark selected orders as Shipped")
    def mark_shipped(self, request, queryset):
        queryset.update(status="shipped")

    @admin.action(description="Mark selected orders as Delivered")
    def mark_delivered(self, request, queryset):
        queryset.update(status="delivered")

    @admin.action(description="Mark selected orders as Cancelled")
    def mark_cancelled(self, request, queryset):
        queryset.update(status="cancelled")
