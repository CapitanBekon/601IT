from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/secure/', views.login_secure_view, name='login_secure'),
    path('login/insecure/', views.login_insecure_view, name='login_insecure'), # Insecure path
    path('store/secure/', views.store_secure_view, name='store_secure'),
    path('store/insecure/', views.store_insecure_view, name='store_insecure'), # Insecure path
    path('cart/', views.cart_view, name='cart'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
]
