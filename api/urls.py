# api_urls.py
from django.urls import path
from .views import (
    SignupAPI, LoginAPI, HelloAPI,
    ExpenseListAPI, ExpenseCreateAPI,
    ExpenseUpdateAPI, ExpenseDeleteAPI
)

urlpatterns = [
    path('signup/', SignupAPI.as_view(), name='api_signup'),
    path('login/', LoginAPI.as_view(), name='api_login'),
    path('hello/', HelloAPI.as_view(), name='hello'),
    path('expenses/', ExpenseListAPI.as_view(), name='expenses'),
    path('expenses/create/', ExpenseCreateAPI.as_view(), name='api_add_expense'),  # Note "create"
    path('expenses/update/<int:id>/', ExpenseUpdateAPI.as_view(), name='update_expense'),
    path('expenses/delete/<int:id>/', ExpenseDeleteAPI.as_view(), name='delete_expense'),
]
