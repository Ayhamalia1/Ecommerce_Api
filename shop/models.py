from django.db import models
from account.models import User

class Category(models.Model):
    name=models.CharField(max_length=20)
    
    def __str__(self):
        return self.name
class Product(models.Model):
    name=models.CharField(max_length=100)
    descreption =models.TextField(blank=True)
    category=models.ForeignKey(Category ,on_delete=models.SET_NULL, null=True,related_name='products')
    price =models.DecimalField(max_digits=7 ,decimal_places=2)
    stock =models.PositiveIntegerField(default=0)
    created_at =models.DateTimeField(auto_now_add=True)
    image=models.ImageField(upload_to='products/', blank=True, null=True)
    def __str__(self):
        return self.name
class Order(models.Model):
    ORDER_STATUS=[
        ('pending', 'قيد الانتظار'),
        ('processing', 'قيد المعالجة'),
        ('shipped', 'تم الشحن'),
        ('delivered', 'تم التوصيل'),
        ('completed', 'مكتمل'), 
        ('cancelled', 'ملغي')
    ]
    user=models.ForeignKey(User ,on_delete=models.CASCADE,related_name='orders')
    address = models.TextField()
    status=models.CharField(max_length=20,choices=ORDER_STATUS ,default='pending')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"
    
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2 )

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"
class Cart(models.Model):
        user = models.OneToOneField(User ,on_delete=models.CASCADE)
        created_at =models.DateTimeField(auto_now_add=True)
        def __str__(self):
            return self.user.username
    
class CartItems(models.Model):
        cart =models.ForeignKey(Cart ,on_delete=models.CASCADE ,related_name='items')
        product =models.ForeignKey(Product , on_delete=models.CASCADE)
        quantity=models.PositiveIntegerField(default=1)
        def __str__(self):
            return f"{self.product.name} x {self.quantity} "
        
        

        @property
        def total_price(self):
         return self.product.price * self.quantity


        
        
    