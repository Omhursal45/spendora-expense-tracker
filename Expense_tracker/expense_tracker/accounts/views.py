from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import SignupSerializer, LoginSerializer
from django.contrib import messages


<<<<<<< HEAD
=======
# ---------------------
# TEMPLATE VIEWS
# ---------------------

>>>>>>> 1da35822626378c190b037b04eb757b0426bd0bf
def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect("/")  # redirect to home
        else:
            return render(request, "registration/login.html", {
                "error": "Invalid username or password"
            })

    return render(request, "registration/login.html")


def signup_page(request):

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
<<<<<<< HEAD
        password = request.POST.get("password1")
        confirm_password = request.POST.get("password2")
=======
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
>>>>>>> 1da35822626378c190b037b04eb757b0426bd0bf

        if password != confirm_password:
            return render(request, "registration/signup.html", {
                "error": "Passwords do not match"
            })

        if User.objects.filter(username=username).exists():
            return render(request, "registration/signup.html", {
                "error": "Username already taken"
            })

        if User.objects.filter(email=email).exists():
            return render(request, "registration/signup.html", {
                "error": "Email already registered"
            })

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect("login")

    return render(request, "registration/signup.html")


# ---------------------
# API VIEWS
# ---------------------

class SignupAPI(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "User created"}, status=201)
        return Response(serializer.errors, status=400)


class LoginAPI(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)
            return Response({"msg": "Login success"}, status=200)

        return Response(serializer.errors, status=400)
