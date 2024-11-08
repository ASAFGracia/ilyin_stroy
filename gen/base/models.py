from django.db import models


class ProductCategory(models.Model):
    category_name = models.CharField(max_length=100)
    category_description = models.TextField(null=True, blank=True)
    category_created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category_name

class Product(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=100)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    markup = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    quantity = models.IntegerField(null=True)

    def __str__(self):
        return self.product_name

class Supplier(models.Model):
    supplier_name = models.CharField(max_length=100)
    supplier_contact = models.CharField(max_length=100, null=True, blank=True)
    supplier_city = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.supplier_name

class ProductSupplier(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2)
    supply_date = models.DateField()

    class Meta:
        unique_together = ('product', 'supplier')

class Client(models.Model):
    client_name = models.CharField(max_length=100)
    client_phone = models.CharField(max_length=20, null=True, blank=True)
    client_email = models.EmailField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.client_name

class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    order_datetime = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=50)

    def __str__(self):
        return f"Order {self.id} - {self.order_status}"

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('order', 'product')

class Service(models.Model):
    service_name = models.CharField(max_length=100)
    service_cost = models.DecimalField(max_digits=10, decimal_places=2)
    completion_time = models.DurationField()

    def __str__(self):
        return self.service_name

class Worker(models.Model):
    worker_name = models.CharField(max_length=100)
    worker_age = models.IntegerField()
    worker_commission = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.worker_name

class OrderService(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True)
    service_cost = models.DecimalField(max_digits=10, decimal_places=2)
    completion_date = models.DateField()

    class Meta:
        unique_together = ('order', 'service', 'worker')

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Payment {self.id} - {self.payment_method}"
