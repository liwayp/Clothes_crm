# models.py
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class UserProfile(models.Model):
    """Расширение профиля пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Аватар")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    position = models.CharField(max_length=100, blank=True, verbose_name="Должность")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
    
    def __str__(self):
        return f"Профиль {self.user.username}"

class Customer(models.Model):
    """Модель клиента"""
    name = models.CharField(max_length=255, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    address = models.TextField(blank=True, verbose_name="Адрес")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Создал")
    
    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('customer_detail', kwargs={'pk': self.pk})

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершен'),
    ]
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Клиент"
    )
    product_name = models.CharField(max_length=200, verbose_name="Название товара")
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Создал")
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заказ #{self.pk} - {self.product_name}"
    
    def get_absolute_url(self):
        return reverse('order_detail', kwargs={'pk': self.pk})
    
    def get_status_display_ru(self):
        status_map = {
            'new': 'Новый',
            'in_progress': 'В процессе',
            'completed': 'Завершен',
        }
        return status_map.get(self.status, self.status)

class Note(models.Model):
    """Заметки к заказам"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='notes', verbose_name="Заказ")
    author = models.CharField(max_length=100, verbose_name="Автор")
    text = models.TextField(verbose_name="Текст заметки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Создал")
    
    class Meta:
        verbose_name = "Заметка"
        verbose_name_plural = "Заметки"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заметка к заказу #{self.order.pk}"

# Сигналы для автоматического создания профиля
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()