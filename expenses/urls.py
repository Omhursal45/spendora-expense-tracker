from django.urls import path
from . import views
from django.contrib.auth import views as registration_views

urlpatterns = [
    # Auth & Profile
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    
    # Password reset/change
    path('change-password/',
        registration_views.PasswordChangeView.as_view(
            template_name='change_password.html',
            success_url='/profile/'
        ),
        name='change_password'
    ),
    path('forgot-password/',
        registration_views.PasswordResetView.as_view(
            template_name="registration/password_reset.html",
            email_template_name="registration/password_reset_email.html",
            success_url='/forgot-password-sent/'
        ),
        name='forgot_password'
    ),
    path('forgot-password-sent/', 
        registration_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_sent.html"),
        name='password_reset_done'
    ),
    path('reset/<uidb64>/<token>/',
        registration_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"),
        name='password_reset_confirm'
    ),
    path('reset/done/',
        registration_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"),
        name='password_reset_complete'
    ),

    # Expense
    path('add-expense/', views.add_expense, name='add_expense'),
    path('view-expenses/', views.view_expenses, name='view_expenses'),
    path('edit-expense/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('delete-expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),

    # Wallets
    path('wallets/create/', views.create_wallet, name='wallet-create'),          
    path('wallets/', views.wallet_list, name='wallet-list'),                    
    path("wallet/<int:pk>/", views.wallet_detail, name="wallet-detail"), 
    path('wallets/<int:wallet_id>/dashboard/', views.wallet_dashboard, name='wallet-dashboard'),
    path('wallets/<int:wallet_id>/add-expense/', views.add_wallet_expense, name='add-wallet-expense'),
    path('wallet-help/', views.wallet_help, name='wallet-help'),
    path('expense-help/',views.expense_help, name='expense-help'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    
    path('analytics/', views.analytics_view, name='analytics'),
    path('budgets/', views.budget_view, name='budgets'),
    path('budgets/add/', views.add_budget, name='add_budget'),
]
