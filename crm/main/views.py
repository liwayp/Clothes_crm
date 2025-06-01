# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.forms import ModelForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Customer, Order, Note, UserProfile

# Authentication Views
class LoginView(forms.Form):
    """Форма входа"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )

def login_view(request):
    """Страница входа"""
    if request.user.is_authenticated:
        return redirect('customer_list')
    
    if request.method == 'POST':
        form = LoginView(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                next_url = request.GET.get('next', 'customer_list')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginView()
    
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')

class RegisterForm(UserCreationForm):
    """Форма регистрации"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })

def register_view(request):
    """Страница регистрации"""
    if request.user.is_authenticated:
        return redirect('customer_list')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})

# Forms
class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter customer name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter address'}),
        }

class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'product_name', 'quantity', 'status']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter quantity'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        customer_id = kwargs.pop('customer_id', None)
        super().__init__(*args, **kwargs)
        
        if customer_id:
            self.fields['customer'].initial = customer_id

class NoteForm(ModelForm):
    class Meta:
        model = Note
        fields = ['author', 'text']
        widgets = {
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter your note...'}),
        }

# Main Views
class CustomerListView(LoginRequiredMixin, ListView):
    """Главная страница - список всех клиентов"""
    model = Customer
    template_name = 'customer_list.html'
    context_object_name = 'customer_list'
    paginate_by = 20
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        thirty_days_ago = now - timezone.timedelta(days=30)
        
        context['new_customers_count'] = Customer.objects.filter(
            created_at__gte=current_month_start
        ).count()
        
        context['active_customers_count'] = Customer.objects.filter(
            orders__created_at__gte=thirty_days_ago
        ).distinct().count()
        
        context['total_orders_count'] = Order.objects.count()
        context['recent_orders'] = Order.objects.select_related('customer').order_by('-created_at')[:5]
        context['total_customers'] = Customer.objects.count()
        context['total_orders'] = Order.objects.count()
        context['today'] = timezone.now().date()
        
        return context

class CustomerDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр клиента + его заказы"""
    model = Customer
    template_name = 'customer_detail.html'
    context_object_name = 'customer'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_object()
        context['orders'] = customer.orders.all().order_by('-created_at')
        context['orders_count'] = customer.orders.count()
        context['completed_orders'] = customer.orders.filter(status='completed').count()
        context['pending_orders'] = customer.orders.exclude(status='completed').count()
        return context

class OrderDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр заказа + форма добавления заметки"""
    model = Order
    template_name = 'order_detail.html'
    context_object_name = 'order'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        context['notes'] = order.notes.all().order_by('-created_at')
        context['note_form'] = NoteForm()
        return context

    def post(self, request, *args, **kwargs):
        order = self.get_object()
        note_form = NoteForm(request.POST)
        
        if note_form.is_valid():
            note = note_form.save(commit=False)
            note.order = order
            note.created_by = request.user
            note.save()
            messages.success(request, 'Note added successfully!')
            return HttpResponseRedirect(reverse('order_detail', kwargs={'pk': order.pk}))
        else:
            context = self.get_context_data()
            context['note_form'] = note_form
            return self.render_to_response(context)

class CustomerCreateView(LoginRequiredMixin, CreateView):
    """Форма создания нового клиента"""
    model = Customer
    form_class = CustomerForm
    template_name = 'customer_form.html'
    success_url = reverse_lazy('customer_list')
    login_url = 'login'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Customer "{form.instance.name}" created successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        return context

class OrderCreateView(LoginRequiredMixin, CreateView):
    """Форма создания нового заказа"""
    model = Order
    form_class = OrderForm
    template_name = 'order_form.html'
    login_url = 'login'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        customer_id = self.request.GET.get('customer')
        if customer_id:
            kwargs['customer_id'] = customer_id
        return kwargs

    def get_success_url(self):
        return reverse('order_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Order "{form.instance.product_name}" created successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        
        customer_id = self.request.GET.get('customer')
        if customer_id:
            try:
                context['preselected_customer'] = Customer.objects.get(pk=customer_id)
            except Customer.DoesNotExist:
                pass
        
        return context

# Additional views
@login_required
def dashboard_stats(request):
    """API для получения статистики дашборда"""
    stats = {
        'total_customers': Customer.objects.count(),
        'total_orders': Order.objects.count(),
        'new_orders': Order.objects.filter(status='new').count(),
        'in_progress_orders': Order.objects.filter(status='in_progress').count(),
        'completed_orders': Order.objects.filter(status='completed').count(),
        'recent_customers': Customer.objects.count() - Customer.objects.filter(
            created_at__lt=timezone.now() - timezone.timedelta(days=30)
        ).count(),
    }
    return JsonResponse(stats)

@login_required
def search_customers(request):
    """Поиск клиентов"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return redirect('customer_list')
    
    customers = Customer.objects.filter(name__icontains=query).distinct()
    
    context = {
        'customer_list': customers,
        'query': query,
        'total_customers': customers.count(),
        'today': timezone.now().date(),
    }
    
    return render(request, 'customer_list.html', context)

@login_required
def update_order_status(request, pk):
    """Быстрое обновление статуса заказа"""
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in ['new', 'in_progress', 'completed']:
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {order.get_status_display()}!')
        else:
            messages.error(request, 'Invalid status!')
    
    return redirect('order_detail', pk=pk)

@login_required
def delete_note(request, note_id):
    """Удаление заметки"""
    if request.method == 'POST':
        note = get_object_or_404(Note, pk=note_id)
        order_pk = note.order.pk
        note.delete()
        messages.success(request, 'Note deleted successfully!')
        return redirect('order_detail', pk=order_pk)
    
    return redirect('customer_list')