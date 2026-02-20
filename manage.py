#!/usr/bin/env python
import os
import sys
import django

if __name__ == "__main__":
    # Change to Expense_tracker directory
    expense_tracker_dir = os.path.join(os.path.dirname(__file__), 'Expense_tracker')
    os.chdir(expense_tracker_dir)
    
    # Add current directory to Python path
    sys.path.insert(0, expense_tracker_dir)
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings')
    
    from django.core.management import execute_from_command_line
    
    execute_from_command_line(sys.argv)
