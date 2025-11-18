from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from expenses.models import Expense
from expenses.serializers import ExpenseSerializer

class HelloAPI(APIView):
    def get(self, request):
        return Response({"msg": "DRF working inside expense tracker!"})


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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpenseUpdateAPI(APIView):
    def put(self, request, id):
        try:
            expense = Expense.objects.get(id=id)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found!"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ExpenseSerializer(expense, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpenseDeleteAPI(APIView):
    def delete(self, request, id):
        try:
            expense = Expense.objects.get(id=id)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found!"}, status=status.HTTP_404_NOT_FOUND)

        expense.delete()
        return Response({"msg": "Expense deleted successfully!"}, status=status.HTTP_200_OK)
    
    
