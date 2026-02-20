from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
from .models import Expense
from .form import ExpenseForm
from django.views.decorators.cache import never_cache
from django.utils.timezone import now
from django.db.models.functions import TruncMonth
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Email imports
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Validation
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

        # Create user
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

@never_cache
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("login")

@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date_created')

    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    total_items = expenses.count()
    total_categories = expenses.values('category').distinct().count()

    # Category chart
    categories = list(expenses.values_list('category', flat=True).distinct())
    category_totals = [
        expenses.filter(category=cat).aggregate(total=Sum('amount'))['total'] or 0
        for cat in categories
    ]

    # Monthly chart (last 6 months)
    start_date = datetime.today() - relativedelta(months=5)
    last_6_months = expenses.filter(date_created__gte=start_date).annotate(
        month=TruncMonth('date_created')
    ).values('month').annotate(total=Sum('amount')).order_by('month')

    months = []
    monthly_totals = []
    monthly_dict = {entry['month'].strftime('%b %Y'): entry['total'] for entry in last_6_months}

    for i in range(5, -1, -1):
        month_date = datetime.today() - relativedelta(months=i)
        month_label = month_date.strftime('%b %Y')
        months.append(month_label)
        monthly_totals.append(monthly_dict.get(month_label, 0))

    context = {
        'expenses': expenses[:10],  
        'total_expense': total_expense,
        'total_items': total_items,
        'total_categories': total_categories,
        'categories': categories,
        'category_totals': category_totals,
        'months': months,
        'monthly_totals': monthly_totals,
    }

    return render(request, 'dashboard.html', context)

@login_required
def add_expense(request):
    user = request.user
    expenses = Expense.objects.filter(user=user)

    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = user
            expense.save()
            return redirect('add_expense')
    else:
        form = ExpenseForm()

    # Metrics
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    monthly_expense = expenses.filter(date_created__month=datetime.now().month,
                                    date_created__year=datetime.now().year).aggregate(total=Sum('amount'))['total'] or 0
    avg_expense = round(total_expense / expenses.count(), 2) if expenses.exists() else 0
    max_expense = expenses.aggregate(max_amount=Sum('amount'))['max_amount'] or 0
    total_items = expenses.count()
    categories = list(expenses.values_list('category', flat=True).distinct())
    category_totals = [expenses.filter(category=c).aggregate(total=Sum('amount'))['total'] or 0 for c in categories]

    # Top 3 categories
    top_categories_qs = expenses.values('category').annotate(total=Sum('amount')).order_by('-total')[:3]
    top_categories = [(c['category'], c['total']) for c in top_categories_qs]

    context = {
        'form': form,
        'total_expense': total_expense,
        'monthly_expense': monthly_expense,
        'avg_expense': avg_expense,
        'max_expense': max_expense,
        'total_items': total_items,
        'categories': categories,
        'category_totals': category_totals,
        'top_categories': top_categories,
    }
    return render(request, 'expenses/add_expense.html', context)


@login_required
def view_expenses(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date_created')
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


@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)

    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated successfully!")
            return redirect("view_expenses")
    else:
        form = ExpenseForm(instance=expense)

    return render(request, "expenses/edit_expense.html", {"form": form})

@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == "POST":
        expense.delete()
        messages.success(request, "Expense deleted successfully!")
        return redirect("view_expenses")
    return render(request, "expenses/confirm_delete.html", {"expense": expense})

@login_required
def profile(request):
    user = request.user
    expenses = Expense.objects.filter(user=user)

    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    total_items = expenses.count()
    avg_expense = round(total_expense / total_items, 2) if total_items else 0
    max_expense = expenses.aggregate(max_amount=Sum('amount'))['max_amount'] or 0
    total_categories = expenses.values('category').distinct().count()

    # Monthly expense
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_expense = expenses.filter(
        date_created__month=current_month,
        date_created__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or 0

    categories = list(expenses.values_list('category', flat=True).distinct())
    category_totals = [
        expenses.filter(category=cat).aggregate(total=Sum('amount'))['total'] or 0
        for cat in categories
    ]

    start_date = datetime.today() - relativedelta(months=5)
    last_6_months = expenses.filter(date_created__gte=start_date).annotate(
        month=TruncMonth('date_created')
    ).values('month').annotate(total=Sum('amount')).order_by('month')

    # Prepare months & totals
    months = []
    monthly_totals = []
    monthly_dict = {entry['month'].strftime('%b %Y'): entry['total'] for entry in last_6_months}

    for i in range(5, -1, -1):
        month_date = datetime.today() - relativedelta(months=i)
        month_label = month_date.strftime('%b %Y')
        months.append(month_label)
        monthly_totals.append(monthly_dict.get(month_label, 0))

    context = {
        'total_expense': total_expense,
        'monthly_expense': monthly_expense,
        'avg_expense': avg_expense,
        'max_expense': max_expense,
        'total_items': total_items,
        'total_categories': total_categories,
        'categories': categories,
        'category_totals': category_totals,
        'months': months,
        'monthly_totals': monthly_totals,
    }

    return render(request, 'profile.html', context)

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

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully!")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "change_password.html", {"form": form})
