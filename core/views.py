from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect
from .models import Product, UserProfile, Order
import hashlib
import base64
import json
import logging

logger = logging.getLogger(__name__)

# --- Helper Functions ---

def get_insecure_user(request):
    token = request.COOKIES.get("insecure_sess")
    if not token:
        return None
    try:
        data = json.loads(base64.b64decode(token).decode())
        return data
    except:
        return None

def get_insecure_cart(request):
    cart_cookie = request.COOKIES.get("insecure_cart")
    if not cart_cookie:
        return {}
    try:
        return json.loads(base64.b64decode(cart_cookie).decode())
    except:
        return {}

def set_insecure_cart_cookie(response, cart_data):
    token = base64.b64encode(json.dumps(cart_data).encode()).decode()
    response.set_cookie("insecure_cart", token, httponly=False, samesite="Lax")

# --- Secure Views ---

def home(request):
    return render(request, "home.html")

def login_secure_view(request):
    if request.method == "POST":
        u = request.POST.get("username")
        p = request.POST.get("password")
        # Secure Authentication using Django built-in secure hashing
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect("store_secure") # Redirect to secure store
        else:
            return render(request, "login_secure.html", {"error": "Invalid credentials"})
    return render(request, "login_secure.html")

@login_required
def store_secure_view(request):
    # Secure: Uses Django ORM (safe from SQLi)
    products = Product.objects.all()
    
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        qty = int(request.POST.get("qty", 1))
        # Validate product
        if Product.objects.filter(id=product_id).exists():
            cart = request.session.get("cart", {})
            current_qty = cart.get(str(product_id), 0)
            cart[str(product_id)] = current_qty + qty
            request.session["cart"] = cart
            # Security: Session modified flag
            request.session.modified = True
            return redirect("cart")
            
    return render(request, "store_secure.html", {"products": products, "user": request.user})

def logout_view(request):
    logout(request)
    response = redirect("home")
    response.delete_cookie("insecure_sess")
    response.delete_cookie("insecure_cart")
    return response

# --- Insecure Views ---

@csrf_exempt
def login_insecure_view(request):
    # Vulnerability: CSRF protection disabled
    error = None
    if request.method == "POST":
        u = request.POST.get("username", "")
        p = request.POST.get("password", "")
        
        # Vulnerability: Weak hashing (MD5)
        p_hash = hashlib.md5(p.encode()).hexdigest()
        
        # Vulnerability: SQL Injection via string concatenation
        query = f"SELECT u.id, u.username FROM auth_user u JOIN core_userprofile p ON u.id = p.user_id WHERE u.username = \"{u}\" AND p.password_insecure = \"{p_hash}\""
        
        logger.warning(f"Executing Insecure Query: {query}")
        
        with connection.cursor() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone() 
                
                if row:
                    user_id, username = row
                    # Vulnerability: Insecure Session (Cookie based, plain encoded)
                    session_data = {"user_id": user_id, "username": username, "role": "user"}
                    if username == "admin":
                        session_data["role"] = "admin"
                        
                    token = base64.b64encode(json.dumps(session_data).encode()).decode()
                    
                    response = redirect("store_insecure")
                    # Vulnerability: HttpOnly=False so JS can read it
                    response.set_cookie("insecure_sess", token, httponly=False, samesite="Lax")
                    return response
                else:
                    error = "Invalid username or password (Insecure Check)"
            except Exception as e:
                # Vulnerability: Verbose Error Messages (SQL Errors exposed)
                error = f"Database Error: {str(e)}"

    return render(request, "login_insecure.html", {"error": error})

@csrf_exempt
def store_insecure_view(request):
    user_data = get_insecure_user(request)
    if not user_data:
        return redirect("login_insecure")
    
    # Handle Add to Cart (Insecure Implementation)
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        qty = int(request.POST.get("qty", 1))
        
        cart = get_insecure_cart(request)
        current_qty = cart.get(str(product_id), 0)
        cart[str(product_id)] = current_qty + qty
        
        response = redirect("cart")
        set_insecure_cart_cookie(response, cart)
        return response

    # Vulnerability: SQL Injection in Search (GET param)
    search_query = request.GET.get("q", "")
    if search_query:
         # Vulnerability: Direct SQL concatenation
         raw_sql = f"SELECT * FROM core_product WHERE name LIKE \"%{search_query}%\""
         products = Product.objects.raw(raw_sql)
    else:
        products = Product.objects.all()

    return render(request, "store_insecure.html", {"products": products, "user": user_data, "search_q": search_query})

# --- Unified Cart View ---

@csrf_exempt # Needed because Insecure post to remove/update might not have token
def cart_view(request):
    # Determine context: Secure vs Insecure
    is_secure = request.user.is_authenticated
    insecure_user = get_insecure_user(request)

    cart_items = []
    total = 0.0
    context_mode = "unknown"
    user = None

    if is_secure:
        # Secure Path: Read from Redis/DB Session
        cart = request.session.get("cart", {})
        for pid, qty in cart.items():
            try:
                p = Product.objects.get(id=pid)
                total += float(p.price) * qty
                cart_items.append({"product": p, "qty": qty, "subtotal": float(p.price) * qty})
            except Product.DoesNotExist:
                continue
        user = request.user
        context_mode = "secure"

    elif insecure_user:
        # Insecure Path: Read from Client Cookie
        cart = get_insecure_cart(request)
        for pid, qty in cart.items():
            # Vulnerability checker: user might inject huge qty or invalid pid
            # We will render it anyway
            try:
                # Even here, we used ORM to fetch name/price, 
                # but an insecure real-world app might trust the price from the cookie too!
                # For this demo, let assumes we trust the ID but fetch details.
                p = Product.objects.get(id=pid)
                total += float(p.price) * qty
                cart_items.append({"product": p, "qty": qty, "subtotal": float(p.price) * qty})
            except Product.DoesNotExist:
                 continue
        user = insecure_user
        context_mode = "insecure"
    else:
        return redirect("home") # Not logged in

    # Handle Remove / Update (Unified Handler)
    if request.method == "POST":
        pid = request.POST.get("product_id")
        action = request.POST.get("action")
        
        if context_mode == "secure":
            cart = request.session.get("cart", {})
            if action == "remove":
                if pid in cart: del cart[pid]
            request.session["cart"] = cart
            request.session.modified = True
            return redirect("cart")
            
        elif context_mode == "insecure":
            cart = get_insecure_cart(request)
            if action == "remove":
                if pid in cart: del cart[pid]
            
            response = redirect("cart")
            set_insecure_cart_cookie(response, cart)
            return response

    return render(request, "cart.html", {
        "cart_items": cart_items, 
        "total": total, 
        "user": user, 
        "mode": context_mode
    })


# --- Admin Dashboard ---
@user_passes_test(lambda u: u.is_superuser)
def dashboard_view(request):
    users = User.objects.all().select_related("profile")
    return render(request, "dashboard.html", {"users": users})

def register_view(request):
    if request.method == "POST":
        u = request.POST.get("username")
        p = request.POST.get("password")
        cp = request.POST.get("confirm_password")
        
        if p != cp:
             return render(request, "register.html", {"error": "Passwords do not match."})

        if User.objects.filter(username=u).exists():
           return render(request, "register.html", {"error": "User with this username already exists."})
        
        # Create standard user - SECURE PATH
        # Django automatically uses PBKDF2 or configured secure hasher
        user = User.objects.create_user(username=u, password=p) 
        
        # Create insecure profile - INSECURE PATH (For Demo Only)
        # We deliberately hash the password with MD5 and store it separately
        # so the user can use the Insecure Login page.
        profile = UserProfile(user=user)
        # Vulnerability: Storing weak hash derived from plaintext
        hashed = hashlib.md5(p.encode()).hexdigest()
        profile.password_insecure = hashed
        profile.save()
        
        # Automatically log the user in via the SECURE method
        login(request, user) 
        return redirect("home")

    return render(request, "register.html")