from django.urls import path
from .views import ExpenseListView, ExpenseDetailView, ExpenseCreateView, ExpenseUpdateView, ExpenseDeleteView, visualizations
from . import views

urlpatterns = [
    path('', ExpenseListView.as_view(), name='home'),
    path('expense/<int:pk>/', ExpenseDetailView.as_view(), name='expense-detail'),
    path('expense/new/', ExpenseCreateView.as_view(), name='expense-create'),
    path('expense/<int:pk>/update/', ExpenseUpdateView.as_view(), name='expense-update'),
    path('expense/<int:pk>/delete/', ExpenseDeleteView.as_view(), name='expense-delete'),
    path('visualizations/', visualizations, name='visualizations'),
    path('download/', views.download_expense_data, name='download_expense_data'),
]