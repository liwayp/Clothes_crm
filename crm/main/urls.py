# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Main pages (требуют авторизации)
    path('', views.CustomerListView.as_view(), name='customer_list'),
    
    # Customers
    path('customers/', views.CustomerListView.as_view(), name='customer_list'),
    path('customers/<int:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    path('customers/add/', views.CustomerCreateView.as_view(), name='customer_add'),
    
    # Orders
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/add/', views.OrderCreateView.as_view(), name='order_add'),
    path('orders/<int:pk>/update-status/', views.update_order_status, name='update_order_status'),
    
    # Search and API
    path('search/', views.search_customers, name='search_customers'),
    path('api/dashboard-stats/', views.dashboard_stats, name='dashboard_stats'),
    
    # Notes
    path('notes/<int:note_id>/delete/', views.delete_note, name='delete_note'),
]