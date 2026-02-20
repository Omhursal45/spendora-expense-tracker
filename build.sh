#!/bin/bash

cd Expense_tracker
python manage.py collectstatic --no-input
python manage.py migrate
