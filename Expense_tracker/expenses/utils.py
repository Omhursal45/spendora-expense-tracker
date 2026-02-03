# expenses/utils.py
from django.core.mail import send_mail
from django.utils import timezone
from .models import Bill

def send_bill_reminders():
    today = timezone.now().date()
    upcoming_bills = Bill.objects.filter(paid=False, due_date__lte=today + timezone.timedelta(days=3))

    for bill in upcoming_bills:
        subject = f"Upcoming Bill Reminder: {bill.title}"
        message = (
            f"Hi {bill.user.username},\n\n"
            f"Your bill '{bill.title}' of ₹{bill.amount} is due on {bill.due_date}.\n"
            "Please pay it on time to avoid late fees.\n\n"
            "Regards,\nExpense Tracker"
        )
        send_mail(subject, message, 'spendora.notify@gmail.com', [bill.user.email])
