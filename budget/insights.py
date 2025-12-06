from datetime import datetime, timedelta
from expenses.models import Expense
from .models import Insight
from django.db.models import Sum

def generate_insights(user):
    today = datetime.today().date()
    week_ago = today - timedelta(days=7)
    two_weeks_ago = today - timedelta(days=14)

    # 1. Weekly change
    this_week = Expense.objects.filter(
        user=user,
        date_created__gte=week_ago
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    last_week = Expense.objects.filter(
        user=user,
        date_created__gte=two_weeks_ago,
        date_created__lt=week_ago
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    if last_week > 0:
        change = ((this_week - last_week) / last_week) * 100
        Insight.objects.create(
            user=user,
            message=f"You spent {change:.1f}% {'more' if change > 0 else 'less'} this week."
        )

    # 2. Highest category (all-time)
    top_cat = (
        Expense.objects.filter(user=user)
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
        .first()
    )

    if top_cat:
        Insight.objects.create(
            user=user,
            message=f"Highest spending category: {top_cat['category']} (₹{top_cat['total']})."
        )

    # 3. Large transaction alert
    last_expense = Expense.objects.filter(user=user).order_by('-id').first()

    if last_expense and last_expense.amount >= 1000:
        Insight.objects.create(
            user=user,
            message=f"High transaction detected: ₹{last_expense.amount} on {last_expense.category}."
        )

    return True
