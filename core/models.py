from django.db import models
from django.contrib.auth.models import User
import hashlib

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.CharField(max_length=255, blank=True)
    stock_qty = models.IntegerField(default=10)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Insecure password storage (MD5 hash) - Vulnerability: Weak Hashing
    password_insecure = models.CharField(max_length=255, blank=True, null=True)
    
    def set_insecure_password(self, raw_password):
        # Vulnerability: Weak hashing (MD5) without salt
        hashed = hashlib.md5(raw_password.encode()).hexdigest()
        self.password_insecure = hashed
        self.save()

    def __str__(self):
        return f"Profile for {self.user.username}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
