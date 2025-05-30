from django.urls import path
from . import views

urlpatterns = [
    # Главная страница - список клиентов
    path('', views.CustomerListView.as_view(), name='customer_list'),
    
    # Клиенты
    path('customers/<int:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    path('customers/add/', views.CustomerCreateView.as_view(), name='customer_add'),
    path('customers/search/', views.search_customers, name='customer_search'),
    
    # Заказы
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/add/', views.OrderCreateView.as_view(), name='order_add'),
    path('orders/<int:pk>/update-status/', views.update_order_status, name='update_order_status'),
    
    # Заметки
    path('notes/<int:note_id>/delete/', views.delete_note, name='delete_note'),
    
    # API/AJAX endpoints
    path('api/dashboard-stats/', views.dashboard_stats, name='dashboard_stats'),
]