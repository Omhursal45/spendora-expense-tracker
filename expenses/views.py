from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
from .models import Expense, Wallet
from .form import ExpenseForm
from django.views.decorators.cache import never_cache
from django.utils.timezone import now
from django.db.models.functions import TruncMonth
from datetime import datetime
from dateutil.relativedelta import relativedelta
from budget.models import Insight
from django.shortcuts import render
import csv
from django.http import HttpResponse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
# Email imports
# from django.core.mail import EmailMultiAlternatives
# from django.conf import settings
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags

#expense-pdf matplotlip imports

from django.http import HttpResponse
from .models import Expense
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from datetime import datetime
import matplotlib.pyplot as plt

# Wallet views
def expense_help(request):
    return render(request, 'expense_help.html')

def wallet_help(request):
    return render(request, 'wallet_help.html')


@login_required
def wallet_list(request):
    wallets = request.user.wallets.all()
    return render(request, "wallets/wallet_list.html", {"wallets": wallets})

# Create a wallet
@login_required
def create_wallet(request):
    if request.method == "POST":
        name = request.POST.get("name")
        members = request.POST.getlist("members")

        wallet = Wallet.objects.create(
            name=name,
            created_by=request.user,
        )
        wallet.members.add(request.user)

        for m in members:
            user = User.objects.get(id=m)
            wallet.members.add(user)

        messages.success(request, "Wallet created successfully!")
        return redirect("wallet-list")

    users = User.objects.exclude(id=request.user.id)
    return render(request, "wallets/wallet_create.html", {"users": users})  # <-- match file name

def wallet_detail(request, pk):
    wallet = get_object_or_404(Wallet, pk=pk)
    expenses = Expense.objects.filter(wallet=wallet).order_by('-date_created')
    return render(request, "wallets/wallet_detail.html", {
        "wallet": wallet,
        "expenses": expenses
    })

# Wallet dashboard (details)
@login_required
def wallet_dashboard(request, wallet_id):
    wallet = get_object_or_404(Wallet, id=wallet_id)

    if request.user not in wallet.members.all():
        messages.error(request, "You are not a member of this wallet.")
        return redirect("wallet-list")

    expenses = Expense.objects.filter(wallet=wallet).order_by("-date_created")
    total_expense = expenses.aggregate(total=Sum("amount"))["total"] or 0

    # Member-wise contribution
    member_contrib = []
    for member in wallet.members.all():
        amt = expenses.filter(user=member).aggregate(sum=Sum("amount"))["sum"] or 0
        member_contrib.append((member.username, amt))

    # Category totals
    categories = expenses.values_list("category", flat=True).distinct()
    category_totals = [
        expenses.filter(category=c).aggregate(total=Sum("amount"))["total"] or 0
        for c in categories
    ]

    context = {
        "wallet": wallet,
        "expenses": expenses,
        "total_expense": total_expense,
        "member_contrib": member_contrib,
        "categories": categories,
        "category_totals": category_totals,
    }

    return render(request, "wallets/wallet_detail.html", context)

# Add expense to a wallet
@login_required
def add_wallet_expense(request, wallet_id):
    wallet = get_object_or_404(Wallet, id=wallet_id)

    if request.user not in wallet.members.all():
        messages.error(request, "You are not a member of this wallet.")
        return redirect("wallet-list")

    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.wallet = wallet

            selected = form.cleaned_data["category"]
            custom = request.POST.get("custom_category", "").strip()
            if selected == "Other" and custom:
                expense.category = custom

            expense.save()
            messages.success(request, "Expense added successfully!")
            return redirect("wallet-detail", pk=wallet.id)
        else:
            print(form.errors)  # <-- debug validation issues
    else:
        form = ExpenseForm()

    return render(request, "wallets/add_wallet_expense.html", {"form": form, "wallet": wallet})


# Auth view

def home(request):
    return render(request, 'home.html')



from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # -----------------------------
        # VALIDATION
        # -----------------------------
        if not all([username, email, password1, password2]):
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

        # -----------------------------
        # CREATE USER
        # -----------------------------
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        # -----------------------------
        # SEND EMAIL (only locally)
        # -----------------------------
        if os.environ.get("RENDER") != "true":
            try:
                subject = "🎉 Welcome to Spendora — Smart Expense Tracker!"
                from_email = settings.EMAIL_HOST_USER
                to = [email]

                html_content = render_to_string("emails/welcome_email.html", {"username": username})
                text_content = strip_tags(html_content)

                msg = EmailMultiAlternatives(subject, text_content, from_email, to)
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                messages.success(request, "Account created successfully! Check your inbox 💌")
            except Exception as e:
                messages.warning(request, f"Account created, but email couldn't be sent ({e})")
        else:
            # On Render, skip sending email
            print(f"Signup successful for {username}, email skipped on Render.")

        # -----------------------------
        # REDIRECT TO LOGIN
        # -----------------------------
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    # GET request — render signup page
    return render(request, "signup.html")





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

# Dashboard view

@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date_created')
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    total_items = expenses.count()
    total_categories = expenses.values('category').distinct().count()

    categories = list(expenses.values_list('category', flat=True).distinct())
    category_totals = [
        expenses.filter(category=cat).aggregate(total=Sum('amount'))['total'] or 0
        for cat in categories
    ]

    # Monthly chart last 6 months
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

    insights = Insight.objects.filter(user=request.user).order_by('-created_at')[:5]

    context = {
        'expenses': expenses[:10],
        'total_expense': total_expense,
        'total_items': total_items,
        'total_categories': total_categories,
        'categories': categories,
        'category_totals': category_totals,
        'months': months,
        'monthly_totals': monthly_totals,
        'insights': insights,
    }

    return render(request, 'dashboard.html', context)

@login_required
def add_expense(request):
    user = request.user
    expenses = Expense.objects.filter(user=user)
    predefined_categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Education","Other"]

    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = user
            selected_category = request.POST.get("category")
            custom_category = request.POST.get("custom_category", "").strip()
            expense.category = custom_category if selected_category == "Other" and custom_category else selected_category or "Uncategorized"
            expense.save()
            messages.success(request, "Expense added successfully!")
            return redirect('add_expense')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ExpenseForm()

    # Metrics
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    monthly_expense = expenses.filter(date_created__month=datetime.now().month, date_created__year=datetime.now().year).aggregate(total=Sum('amount'))['total'] or 0
    total_items = expenses.count()
    avg_expense = round(total_expense / total_items, 2) if total_items else 0
    max_expense = expenses.aggregate(max_amount=Sum('amount'))['max_amount'] or 0
    categories = sorted(list(expenses.values_list('category', flat=True).distinct()))
    category_totals = [expenses.filter(category=c).aggregate(total=Sum('amount'))['total'] or 0 for c in categories]

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
        'predefined_categories': predefined_categories,
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
    form = ExpenseForm(request.POST or None, instance=expense)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Expense updated successfully!")
        return redirect("view_expenses")
    return render(request, "expenses/edit_expense.html", {"form": form})

@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == "POST":
        expense.delete()
        messages.success(request, "Expense deleted successfully!")
        return redirect("view_expenses")
    return render(request, "expenses/confirm_delete.html", {"expense": expense})

# profile view

@login_required
def profile(request):
    user = request.user
    expenses = Expense.objects.filter(user=user)
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    total_items = expenses.count()
    avg_expense = round(total_expense / total_items, 2) if total_items else 0
    max_expense = expenses.aggregate(max_amount=Sum('amount'))['max_amount'] or 0
    total_categories = expenses.values('category').distinct().count()

    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_expense = expenses.filter(date_created__month=current_month, date_created__year=current_year).aggregate(total=Sum('amount'))['total'] or 0

    categories = list(expenses.values_list('category', flat=True).distinct())
    category_totals = [expenses.filter(category=cat).aggregate(total=Sum('amount'))['total'] or 0 for cat in categories]

    start_date = datetime.today() - relativedelta(months=5)
    last_6_months = expenses.filter(date_created__gte=start_date).annotate(month=TruncMonth('date_created')).values('month').annotate(total=Sum('amount')).order_by('month')
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


@login_required
def export_csv(request):
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

    writer = csv.writer(response)
    writer.writerow(['Title', 'Amount', 'Category', 'Date'])

    # Get expenses for the logged-in user, ordered by creation date
    expenses = Expense.objects.filter(user=request.user).order_by('-date_created')

    for expense in expenses:
        # Use expense.date_created instead of expense.date
        writer.writerow([expense.title, expense.amount, expense.category, expense.date_created])

    return response




def export_pdf(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date_created')
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=100, bottomMargin=50, leftMargin=50, rightMargin=50)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'title',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=1,  # center
        textColor=colors.HexColor("#4f46e5"),
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'subtitle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=1,
        textColor=colors.grey,
        spaceAfter=20
    )
    
    # Header
    elements.append(Paragraph("Spendora – My Expense Tracker", title_style))
    elements.append(Paragraph(f"Report for: {request.user.username}", subtitle_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%d %b %Y, %H:%M')}", subtitle_style))
    
    # Summary
    total_amount = sum([exp.amount for exp in expenses])
    elements.append(Paragraph(f"<b>Total Expenses:</b> ₹{total_amount:.2f}", styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))
    
    # Table Data
    data = [['Title', 'Category', 'Amount (₹)', 'Date']]
    for i, exp in enumerate(expenses):
        row_color = colors.whitesmoke if i % 2 == 0 else colors.lightgrey
        data.append([exp.title, exp.category, f"{exp.amount:.2f}", exp.date_created.strftime('%d %b %Y')])
    
    table = Table(data, colWidths=[7*cm, 4*cm, 3*cm, 4*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4f46e5")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    
    # Alternating row colors
    for i in range(1, len(data)):
        bg_color = colors.whitesmoke if i % 2 == 0 else colors.lightgrey
        table.setStyle([('BACKGROUND', (0,i), (-1,i), bg_color)])
    
    elements.append(table)
    elements.append(Spacer(1, 1*cm))
    
    # Category Pie Chart
    if expenses.exists():
        category_totals = {}
        for exp in expenses:
            category_totals[exp.category] = category_totals.get(exp.category, 0) + exp.amount
        plt.figure(figsize=(4,4))
        plt.pie(category_totals.values(), labels=category_totals.keys(), autopct='%1.1f%%', startangle=140)
        plt.title("Expenses by Category")
        chart_buffer = BytesIO()
        plt.savefig(chart_buffer, format='PNG', bbox_inches='tight')
        plt.close()
        chart_buffer.seek(0)
        elements.append(Image(chart_buffer, width=12*cm, height=12*cm))
    
    # Footer function
    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.setFont('Helvetica', 10)
        canvas.drawRightString(A4[0] - 50, 20, text)

    # Build PDF
    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
    buffer.seek(0)
    
    return HttpResponse(buffer, content_type='application/pdf')
