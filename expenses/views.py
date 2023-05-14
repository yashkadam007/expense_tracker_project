from typing import Optional
from django.forms.models import BaseModelForm
from django.http import Http404, HttpResponse
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Expense

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