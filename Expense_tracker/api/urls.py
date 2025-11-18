from django.urls import path
from .views import HelloAPI,ExpenseListAPI,ExpenseCreateAPI,ExpenseUpdateAPI,ExpenseDeleteAPI

urlpatterns = [
    path('hello/', HelloAPI.as_view()),
    path('expenses/', ExpenseListAPI.as_view()),
    path('expenses/add/', ExpenseCreateAPI.as_view()),
    path('api/expense/update/<int:id>/',ExpenseUpdateAPI.as_view()),
    path('api/expense/delete/<int:id>/',ExpenseDeleteAPI.as_view()),
]