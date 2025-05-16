from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
import re
from .models import Books, User, Order, Cart, OrderItem
from .forms import BookForm, RegisterForm, LoginForm, UserProfileForm
from django.db import transaction
from django.contrib.auth import login as auth_login
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('logform')
    form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def check_login(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)

def check_email(request):
    email = request.GET.get('email', None)
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    data = {
        'is_valid': re.match(email_regex, email) is not None
    }
    return JsonResponse(data)

def check_passwordlen(request):
    password = request.GET.get('password', None)
    data = {
        'is_valid': len(password) >= 6 if password else False
    }
    return JsonResponse(data)

def logform(request):
    return render(request, 'login.html')

@login_required
def add_to_cart(request, pk):
    book = get_object_or_404(Books, pk=pk)
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        book=book,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'{book.title} добавлена в вашу корзину!')
    return redirect('book_list')


@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user).select_related('book')
    for item in cart_items:
        item.display_total = item.total_price
    total_price = sum(item.total_price for item in cart_items)
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


@login_required
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(Cart, pk=pk, user=request.user)
    cart_item.delete()
    messages.success(request, 'Товар удален из корзины')
    return redirect('view_cart')


@login_required
def buy_now(request, book_id):
    book = get_object_or_404(Books, id=book_id)
    order = Order.objects.create(
        user=request.user,
        total_price=book.price
    )
    OrderItem.objects.create(
        order=order,
        book=book,
        quantity=1,
        price=book.price
    )
    messages.success(request, f'Заказ #{order.id} оформлен!')
    return redirect('order_detail', pk=order.id)

@login_required
def create_order(request):
    cart_items = Cart.objects.filter(user=request.user).select_related('book')

    if not cart_items.exists():
        messages.warning(request, 'Ваша корзина пуста!')
        return redirect('book_list')

    with transaction.atomic():
        total_price = sum(
            float(item.book.price) * item.quantity
            for item in cart_items
        )
        order = Order.objects.create(
            user=request.user,
            total_price=total_price
        )
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                book=item.book,
                quantity=item.quantity,
                price=float(item.book.price)
            )
        cart_items.delete()
    messages.success(request, f'Заказ #{order.id} создан. Сумма: {total_price:.2f} руб.')
    return redirect('order_detail', pk=order.pk)

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'order_detail.html', {'order': order})

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_list.html', {'orders': orders})

def book_list(request):
    books = Books.objects.all()
    authors = Books.objects.values_list('author', flat=True).distinct()
    paginator = Paginator(books, 6)  # 6 книг на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    author_filter = request.GET.get('author')
    if author_filter:
        books = books.filter(author__icontains=author_filter)
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        books = books.filter(price__gte=float(price_min))
    if price_max:
        books = books.filter(price__lte=float(price_max))

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, '_book_list.html', {'books': books})

    return render(request, 'book_list.html', {
        'books': books,
        'authors': authors,
        'page_obj': page_obj
    })

@login_required
def book_detail(request, pk):
    book = get_object_or_404(Books, pk=pk)
    return render(request, 'book_detail.html', {'book': book})

@login_required
def book_new(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm()
    return render(request, 'edit_book.html', {'form': form})

@login_required
def book_edit(request, pk):
    book = get_object_or_404(Books, pk=pk)
    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'edit_book.html', {'form': form})

@login_required
def book_delete(request, pk):
    book = get_object_or_404(Books, pk=pk)
    book.delete()
    return redirect('book_list')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('logform')
    form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def logform(request):
    return render(request, 'login.html')

@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('book_list')

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            request.session['last_login'] = str(timezone.now())
            request.session['login_count'] = request.session.get('login_count', 0) + 1
            response = redirect('book_list')
            response.set_cookie(
                'user_preference', 'default_theme',
                max_age=3600 * 24 * 30, secure=True, httponly=True, samesite='Lax'
            )
            messages.success(request, 'Вы успешно вошли!')
            return response
        else:
            messages.error(request, 'Неверный email или пароль')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    if 'last_login' in request.session:
        del request.session['last_login']
    logout(request)
    messages.success(request, 'Вы успешно вышли')
    response = redirect('book_list')
    response.delete_cookie('user_preference')
    response.delete_cookie('bookstore_session')
    return response
@login_required
def increase_quantity(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    messages.success(request, f"Количество {cart_item.book.title} увеличено")
    return redirect('view_cart')

@login_required
def decrease_quantity(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    messages.info(request, f"Количество {cart_item.book.title} уменьшено")
    return redirect('view_cart')

@require_POST
@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.warning(request, 'Ваша корзина пуста!')
        return redirect('cart')
    total = sum(item.book.price * item.quantity for item in cart_items)
    order = Order.objects.create(
        user=request.user,
        total_price=total
    )
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            book=item.book,
            quantity=item.quantity,
            price=item.book.price
        )
    cart_items.delete()
    messages.success(request, f'Заказ #{order.id} оформлен! Сумма: {total:.2f} руб.')
    return redirect('order_detail', pk=order.id)

@csrf_protect
@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('profile')
        else:
            messages.error(request, 'Ошибка в данных формы')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})


@receiver(post_save, sender=User)
def assign_admin_role(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        instance.role = 'admin'
        instance.save()


