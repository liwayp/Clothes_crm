from django.db import models
from django.urls import reverse


class Customer(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя клиента")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.TextField(verbose_name="Адрес")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

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
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
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
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='notes',
        verbose_name="Заказ"
    )
    author = models.CharField(max_length=50, verbose_name="Автор")
    text = models.TextField(verbose_name="Текст заметки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Заметка"
        verbose_name_plural = "Заметки"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заметка от {self.author} к заказу #{self.order.pk}"