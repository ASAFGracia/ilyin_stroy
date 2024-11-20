from django.contrib import admin
from .models import ProductCategory, Product, Supplier, ProductSupplier, Client, Order, OrderProduct, Service, Worker, OrderService, Payment


admin.site.register(ProductSupplier)
admin.site.register(Client)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(Service)
admin.site.register(Worker)
admin.site.register(OrderService)
admin.site.register(Payment)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'purchase_price', 'quantity')
    list_filter = ('category',)
    search_fields = ('product_name',)

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'category_created_at')
    search_fields = ('category_name',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_name', 'supplier_city')
    list_filter = ('supplier_city',)
    search_fields = ('supplier_name',)
