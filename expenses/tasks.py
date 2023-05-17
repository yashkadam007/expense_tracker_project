from celery import shared_task
from .models import Expense
import csv
from io import StringIO
from django.contrib.auth.models import User

@shared_task
def download_expense_data_task(user_id):
    user = User.objects.get(id=user_id)
    expenses = Expense.objects.filter(user=user)

    csv_data = StringIO()
    writer = csv.writer(csv_data)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])
    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category.name, expense.date])

    return csv_data.getvalue()
