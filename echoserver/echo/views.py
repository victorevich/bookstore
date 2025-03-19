from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm, LoginForm
from django.shortcuts import render, get_object_or_404, redirect
from .models import Books
from .forms import BookForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save

def book_list(request):
    books_list = Books.objects.all()
    paginator = Paginator(books_list, 2)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    return render(request, 'book_list.html', {'books': books})
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
            user = form.save()
            login(request, user)
            return redirect('book_list')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('book_list')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('book_list')

@receiver(post_save, sender=User)
def assign_admin_role(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        instance.role = 'admin'
        instance.save()
