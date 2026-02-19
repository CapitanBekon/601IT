import os
import django
import hashlib

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storefront.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile, Product

# Create Admin
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
    profile = UserProfile.objects.create(user=admin)
    profile.set_insecure_password('adminpass')
    print("Admin created (username: admin, pass: adminpass)")

# Create Normal User
if not User.objects.filter(username='user').exists():
    user = User.objects.create_user('user', 'user@example.com', 'userpass')
    profile = UserProfile.objects.create(user=user)
    profile.set_insecure_password('userpass')
    print("User created (username: user, pass: userpass)")

# Create Products
if not Product.objects.exists():
    Product.objects.create(name='Secure Sword', description='A sword forged with typing safety.', price=100.00)
    Product.objects.create(name='Insecure Dagger', description='An ancient dagger with a curse: <script>alert("XSS Vulnerability")</script>. Ensure your browser executes scripts!', price=10.00)
    Product.objects.create(name='SQL Shield', description='Protects against injections.', price=50.00)
    print("Products created.")
