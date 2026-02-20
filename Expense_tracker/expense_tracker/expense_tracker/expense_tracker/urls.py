from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # HTML login/logout and password reset (Django auth)
    path('accounts/', include('django.contrib.auth.urls')),

    # Your HTML pages
    path('', include('expenses.urls')),

    # API endpoints
    path('api/', include('api.urls')),
]
