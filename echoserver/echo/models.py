from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
class Books(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.title
    class Meta:
        db_table = 'books'
        managed = False
class User(AbstractUser):
    ROLES = (
        ('user', 'user'),
        ('admin', 'admin'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='user')
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super(User, self).save(*args, **kwargs)
    def __str__(self):
        return self.username
    class Meta:
        db_table = 'User'


class Cart(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    book = models.ForeignKey(Books, verbose_name='Книга', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField('Количество', default=1)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    def __str__(self):
        return f"Корзина {self.user.username} - {self.book.title}"

    class Meta:
        db_table = 'cart'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class Order(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    items = models.ManyToManyField(Books, through='OrderItem', verbose_name='Товары')
    total_price = models.DecimalField('Общая стоимость', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField('Дата заказа', auto_now_add=True)

    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username}"

    class Meta:
        db_table = 'orders'
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', on_delete=models.CASCADE)
    book = models.ForeignKey(Books, verbose_name='Книга', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField('Количество')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)

    def get_total_item_price(self):
        return self.price * self.quantity
    def __str__(self):
        return f"{self.book.title} в заказе #{self.order.id}"

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'