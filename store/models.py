from django.db import models
from django.contrib.auth.models import User
from django.apps import AppConfig

class Sock(models.Model):
       name = models.CharField(max_length=255)  # Temporarily remove unique=True
       description = models.TextField()
       price = models.DecimalField(max_digits=6, decimal_places=2)
       image = models.ImageField(upload_to='socks/')
       stock = models.PositiveIntegerField(default=0)

       def is_in_stock(self):
           return self.stock > 0
       is_in_stock.boolean = True

       def __str__(self):
           return self.name

class StoreConfig(AppConfig):
       default_auto_field = 'django.db.models.BigAutoField'
       name = 'store'

       def ready(self):
           import store.signals

class Review(models.Model):
       sock = models.ForeignKey(Sock, related_name='reviews', on_delete=models.CASCADE)
       user = models.ForeignKey(User, on_delete=models.CASCADE)
       text = models.TextField()
       rating = models.FloatField(default=5.0, null=True, blank=True)
       photo = models.ImageField(upload_to='reviews/', null=True, blank=True)
       video = models.FileField(upload_to='reviews/', null=True, blank=True)
       created_at = models.DateTimeField(auto_now_add=True)

       def __str__(self):
           return f'Review for {self.sock} by {self.user}'

class Cart(models.Model):
       user = models.OneToOneField(User, on_delete=models.CASCADE)

       def __str__(self):
           return f"{self.user.username}'s Cart"

class CartItem(models.Model):
       user = models.ForeignKey(User, on_delete=models.CASCADE)
       cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
       sock = models.ForeignKey(Sock, on_delete=models.CASCADE)
       quantity = models.PositiveIntegerField(default=1)

       def __str__(self):
           return f"{self.quantity} x {self.sock.name}"

class Profile(models.Model):
       user = models.OneToOneField(User, on_delete=models.CASCADE)
       pfp = models.ImageField(upload_to='profile_pics/', default='default.jpg')

       def __str__(self):
           return f"{self.user.username}'s Profile"

class OrderItem(models.Model):
       sock = models.ForeignKey(Sock, on_delete=models.CASCADE)
       quantity = models.PositiveIntegerField()
       price = models.DecimalField(max_digits=10, decimal_places=2)

       def __str__(self):
           return f"{self.quantity} x {self.sock.name}"

class Order(models.Model):
       user = models.ForeignKey(User, on_delete=models.CASCADE)
       order_time = models.DateTimeField(auto_now_add=True)
       total_amount = models.DecimalField(max_digits=10, decimal_places=2)
       payment_id = models.CharField(max_length=255, blank=True, null=True)
       order_id = models.CharField(max_length=255, blank=True, null=True)
       signature = models.CharField(max_length=255, blank=True, null=True)
       items = models.ManyToManyField(OrderItem)
       name = models.CharField(max_length=255)
       phone = models.CharField(max_length=15)
       email = models.EmailField()
       address1 = models.CharField(max_length=255)
       address2 = models.CharField(max_length=255, blank=True, null=True)
       city = models.CharField(max_length=100)
       postal_code = models.CharField(max_length=10)
       state = models.CharField(max_length=100, null=True, blank=True)  # Made nullable temporarily
       payment_method = models.CharField(max_length=50, choices=[('Credit', 'Credit Card'), ('Debit', 'Debit Card'), ('PayPal', 'PayPal'), ('razorpay', 'Razorpay'), ('cod', 'Cash on Delivery')])
       status = models.CharField(max_length=50, default='Pending')

       def __str__(self):
           return f"Order #{self.id} by {self.user.username}"

       @property
       def get_total_price(self):
           total = sum(item.price * item.quantity for item in self.items.all())
           return total