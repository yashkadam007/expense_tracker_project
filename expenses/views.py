from django.http import Http404, HttpResponse
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Expense, Category
from django.db.models import Sum
from django.contrib import messages
from .insights import generate_pie_chart, generate_line_chart
from django.urls import reverse
from .tasks import download_expense_data_task
from .models import Expense
from django.db.models import Q
from decimal import Decimal
from datetime import datetime
from calendar import month_name





# Create your views here.
# @login_required
# def home(request):
#     expenses = Expense.objects.filter(user=request.user)
#     return render(request, 'expenses/home.html', {'expenses': expenses})

def search_expenses(request):
    search_query = request.GET.get('search')
    expenses = Expense.objects.filter(user=request.user)

    if search_query and search_query.startswith('>'):
        try:
            amount = Decimal(search_query[1:])
            expenses = expenses.filter(amount__gt=amount)
        except ValueError:
            pass
    elif search_query and search_query.startswith('<'):
        try:
            amount = Decimal(search_query[1:])
            expenses = expenses.filter(amount__lt=amount)
        except ValueError:
            pass
    else:
        # Check if the search query represents a month
        month = None
        for index, month_name_str in enumerate(month_name[1:]):
            if search_query.lower() == month_name_str.lower():
                month = index + 1
                break

        if month:
            year = datetime.now().year
            expenses = expenses.filter(date__month=month, date__year=year)
        else:
            expenses = expenses.filter(
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

    context = {
        'expenses': expenses,
        'search_query': search_query
    }
    return render(request, 'expenses/search_expenses.html', context)

@method_decorator(login_required, name='dispatch')
class ExpenseListView(ListView):
    model = Expense
    template_name = 'expenses/home.html'
    context_object_name = 'expenses'
    ordering = ['-date']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['download_url'] = reverse('download_expense_data')
        return context

@method_decorator(login_required, name='dispatch')
class ExpenseDetailView(DetailView):
    model = Expense

    def get_object(self, queryset=None):
        expense = super().get_object(queryset)
        if expense.user != self.request.user:
            raise Http404("You are not authorized to view this expense.")
        return expense

class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    fields = ['amount', 'description', 'category']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    

class ExpenseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Expense
    fields = ['amount', 'description', 'category']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        expense = self.get_object()
        if self.request.user == expense.user:
            return True
        return False
    

class ExpenseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Expense
    success_url = '/'

    def test_func(self):
        expense = self.get_object()
        if self.request.user == expense.user:
            return True
        return False


def visualizations(request):
    curr_user = request.user
    categories = Category.objects.all()
    expenses = Expense.objects.filter(user=curr_user).values('category', 'date').annotate(total=Sum('amount')).order_by('date')

    if not expenses:
        messages.warning(request, f'No expenses found for {curr_user}! Please add expenses to see visualizations')
        return redirect('home')

    expense_data = {}
    x_values = sorted(set([expense['date'].strftime('%Y-%m-%d') for expense in expenses]))

    for expense in expenses:
        category_name = Category.objects.get(pk=expense['category']).name
        if category_name not in expense_data:
            expense_data[category_name] = []
        expense_data[category_name].append(expense['total'])

    total_expenses = Expense.objects.filter(user=curr_user).aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'image_uri': generate_pie_chart(expense_data),
        'image_uri_line_chart': generate_line_chart(expense_data, x_values, expense_data),
        'total_expenses': total_expenses
    }

    return render(request, 'expenses/visualizations.html', context=context)

#  Download without celery
# @login_required
# def download_expense_data(request):
#     expenses = Expense.objects.filter(user=request.user)

#     # Create the CSV file
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="expense_data.csv"'

#     # Write the CSV data
#     writer = csv.writer(response)
#     writer.writerow(['Amount', 'Description', 'Category', 'Date'])
#     for expense in expenses:
#         writer.writerow([expense.amount, expense.description, expense.category.name, expense.date])

#     return response

@login_required
def download_expense_data(request):
    task = download_expense_data_task.delay(request.user.id)
    csv_data = task.get()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expense_data.csv"'
    response.write(csv_data)

    return response