from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),

    path('cart/', views.cart_page, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),

    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:pk>/thank-you/', views.order_thank_you, name='order_thank_you'),

    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),

    path('cart/update/', views.update_cart_quantity, name='update_cart_quantity'),

    path('order/track/', views.order_track, name='order_track'),
    
    path('category/<slug:slug>/', views.category_page, name='category_page'),

    # auth-related
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='siteapp/login.html'
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(
        next_page='home'
    ), name='logout'),

    path('my-orders/', views.my_orders, name='my_orders'),
]

