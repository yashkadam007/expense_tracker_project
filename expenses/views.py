from django.http import Http404
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Expense, Category
from django.db.models import Sum
from django.contrib import messages
from .insights import generate_pie_chart, generate_line_chart




# Create your views here.
@login_required
def home(request):
    expenses = Expense.objects.filter(user=request.user)
    return render(request, 'expenses/home.html', {'expenses': expenses})

@method_decorator(login_required, name='dispatch')
class ExpenseListView(ListView):
    model = Expense
    template_name = 'expenses/home.html'
    context_object_name = 'expenses'
    ordering = ['-date']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

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

    context = {
        'image_uri': generate_pie_chart(expense_data),
        'image_uri_line_chart': generate_line_chart(expense_data, x_values, expense_data)
    }

    return render(request, 'expenses/visualizations.html', context=context)

