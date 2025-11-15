from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-expense/', views.add_expense, name='add_expense'),
    path('view-expenses/', views.view_expenses, name='view_expenses'),
    path('edit-expense/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('delete-expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path(
        'change-password/',
        auth_views.PasswordChangeView.as_view(
            template_name='change_password.html',
            success_url='/profile/'
        ),
        name='change_password'
    ),
    path('forgot-password/', 
        auth_views.PasswordResetView.as_view(template_name="auth/password_reset.html"),
        name='forgot_password'),

    path('forgot-password-sent/', 
        auth_views.PasswordResetDoneView.as_view(template_name="auth/password_reset_sent.html"),
        name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name="auth/password_reset_confirm.html"),
        name='password_reset_confirm'),

    path('reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name="auth/password_reset_complete.html"),
        name='password_reset_complete'),
]

    

