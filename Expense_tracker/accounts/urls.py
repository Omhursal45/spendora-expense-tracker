from django.urls import path
from .views import login_page, signup_page, SignupAPI, LoginAPI

urlpatterns = [
    # Template views
    path("login/", login_page, name="login"),
    path("signup/", signup_page, name="signup"),

    # API views
    path("api/signup/", SignupAPI.as_view(), name="api_signup"),
    path("api/login/", LoginAPI.as_view(), name="api_login"),
]
