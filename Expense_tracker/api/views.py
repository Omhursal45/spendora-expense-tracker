from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from expenses.models import Expense
from expenses.serializers import ExpenseSerializer


class SignupAPI(APIView):
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=400)

        User.objects.create_user(username=username, email=email, password=password)
        return Response({"msg": "User created successfully!"}, status=201)

class LoginAPI(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user:
            return Response({"msg": "Login successful!"}, status=200)
        return Response({"error": "Invalid credentials"}, status=401)

class HelloAPI(APIView):
    def get(self, request):
        return Response({"message": "Spendora API working!"})

class ExpenseListAPI(APIView):
    def get(self, request):
        expenses = Expense.objects.all()
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)

class ExpenseCreateAPI(APIView):
    def post(self, request):
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class ExpenseUpdateAPI(APIView):
    def put(self, request, id):
        try:
            expense = Expense.objects.get(id=id)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found"}, status=404)

        serializer = ExpenseSerializer(expense, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class ExpenseDeleteAPI(APIView):
    def delete(self, request, id):
        expense = get_object_or_404(Expense, id=id)
        expense.delete()
        return Response({"message": "Expense deleted successfully"}, status=status.HTTP_204_NO_CONTENT)