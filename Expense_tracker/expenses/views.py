from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Expense
from .form import ExpenseForm
from django.views.decorators.cache import never_cache

# Email imports
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Sum
from django.db.models.functions import TruncMonth


# Home / Landing page
def home(request):
    return render(request, 'home.html')


#Signup
def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not username or not email or not password1 or not password2:
            messages.error(request, "All fields are required.")
            return redirect('signup')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        # Send welcome email
        subject = "🎉 Welcome to Spendora — Smart Expense Tracker!"
        from_email = settings.EMAIL_HOST_USER
        to = [email]

        html_content = render_to_string("emails/welcome_email.html", {"username": username})
        text_content = strip_tags(html_content)

        try:
            msg = EmailMultiAlternatives(subject, text_content, from_email, to)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            messages.success(request, "Account created successfully! Check your inbox 💌")
        except Exception as e:
            messages.warning(request, f"Account created, but email couldn't be sent ({e})")

        return redirect('login')

    return render(request, 'registration/signup.html')


#Login
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password!")

    return render(request, "registration/login.html")


# LOGOUT
@never_cache
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("login")


# dashboard
@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    total_items = expenses.count()
    
    categories_qs = expenses.values_list('category', flat=True).distinct()
    categories = list(categories_qs)
    category_totals = [expenses.filter(category=cat).aggregate(total=Sum('amount'))['total'] or 0 for cat in categories]
    
    recent_expenses = expenses[:10]
    
    context = {
        'expenses': recent_expenses,
        'total_expense': total_expense,
        'total_categories': len(categories),
        'total_items': total_items,
        'categories': categories,
        'category_totals': category_totals,
    }
    return render(request, 'dashboard.html', context)


# add expense
@login_required
def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, "Expense added!")
            return redirect("view_expenses")
    else:
        form = ExpenseForm()
    return render(request, 'expenses/add_expense.html', {'form': form})


#view expense
@login_required
def view_expenses(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    total_items = expenses.count()
    avg_expense = round(total_expense / total_items, 2) if total_items else 0
    max_expense = expenses.aggregate(max_amount=Sum('amount'))['max_amount'] or 0

    context = {
        'expenses': expenses,
        'total_expenses': total_expense,
        'total_items': total_items,
        'avg_expense': avg_expense,
        'max_expense': max_expense,
    }
    return render(request, 'expenses/view_expenses.html', context)


#edit expense
@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated!")
            return redirect("view_expenses")
    else:
        form = ExpenseForm(instance=expense)
    return render(request, "expenses/edit_expense.html", {"form": form})


#Delete expense
@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == "POST":
        expense.delete()
        messages.success(request, "Expense deleted!")
        return redirect("view_expenses")
    return render(request, "expenses/confirm_delete.html", {"expense": expense})


#profile
@login_required
def profile(request):
    return render(request, "profile.html")


#profile edit
@login_required
def edit_profile(request):
    if request.method == "POST":
        user = request.user
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("profile")
    return render(request, "edit_profile.html")


#change password
@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated!")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "change_password.html", {"form": form})


