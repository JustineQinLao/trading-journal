from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q, Sum, Count, Avg
from datetime import timedelta

from .models import Trade, AccountBalance
from .forms import TradeForm, TradeFilterForm
from .utils import (
    calculate_win_rate, calculate_average_rr, calculate_pnl,
    calculate_expectancy, calculate_return_percentage, get_win_loss_counts, get_best_worst_trades,
    get_streak, get_monthly_pnl, get_statistics_by_category
)


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view showing overview statistics"""
    template_name = 'trades/dashboard.html'
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_trades = Trade.objects.filter(user=self.request.user)
        
        # Get or create account balance
        account_balance, created = AccountBalance.objects.get_or_create(
            user=self.request.user,
            defaults={'balance': 100.00, 'initial_balance': 100.00}
        )
        context['account_balance'] = account_balance.balance
        context['initial_balance'] = account_balance.initial_balance
        
        # Today's stats
        today = timezone.now().date()
        today_trades = user_trades.filter(timestamp__date=today)
        context['today_trades'] = today_trades.count()
        context['today_wins'] = today_trades.filter(outcome='WINNER').count()
        context['today_losses'] = today_trades.filter(outcome='LOSER').count()
        context['today_pnl'] = calculate_pnl(today_trades)
        
        # This week's stats
        week_start = today - timedelta(days=today.weekday())
        week_trades = user_trades.filter(timestamp__date__gte=week_start)
        context['week_trades'] = week_trades.count()
        context['week_wins'] = week_trades.filter(outcome='WINNER').count()
        context['week_losses'] = week_trades.filter(outcome='LOSER').count()
        context['week_pnl'] = calculate_pnl(week_trades)
        context['week_win_rate'] = calculate_win_rate(week_trades)
        context['week_avg_rr'] = calculate_average_rr(week_trades)
        
        # All-time stats
        context['total_trades'] = user_trades.count()
        context['total_wins'] = user_trades.filter(outcome='WINNER').count()
        context['total_losses'] = user_trades.filter(outcome='LOSER').count()
        context['total_pnl'] = calculate_pnl(user_trades)
        context['total_win_rate'] = calculate_win_rate(user_trades)
        context['total_avg_rr'] = calculate_average_rr(user_trades)
        
        # Recent trades
        context['recent_trades'] = user_trades[:5]
        
        return context


class TradeListView(LoginRequiredMixin, ListView):
    """List view with filtering and pagination"""
    model = Trade
    template_name = 'trades/trade_list.html'
    context_object_name = 'trades'
    paginate_by = 20
    login_url = '/admin/login/'
    
    def get_queryset(self):
        queryset = Trade.objects.filter(user=self.request.user)
        
        # Apply filters
        form = TradeFilterForm(self.request.GET)
        if form.is_valid():
            date_from = form.cleaned_data.get('date_from')
            date_to = form.cleaned_data.get('date_to')
            symbol = form.cleaned_data.get('symbol')
            outcome = form.cleaned_data.get('outcome')
            entry_type = form.cleaned_data.get('entry_type')
            direction = form.cleaned_data.get('direction')
            
            if date_from:
                queryset = queryset.filter(timestamp__date__gte=date_from)
            if date_to:
                queryset = queryset.filter(timestamp__date__lte=date_to)
            if symbol:
                queryset = queryset.filter(symbol=symbol)
            if outcome:
                queryset = queryset.filter(outcome=outcome)
            if entry_type:
                queryset = queryset.filter(entry_type=entry_type)
            if direction:
                queryset = queryset.filter(direction=direction)
        
        return queryset.order_by('-timestamp')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = TradeFilterForm(self.request.GET)
        
        # Summary stats for filtered results
        filtered_trades = self.get_queryset()
        context['filtered_count'] = filtered_trades.count()
        context['filtered_pnl'] = calculate_pnl(filtered_trades)
        context['filtered_win_rate'] = calculate_win_rate(filtered_trades)
        context['filtered_avg_rr'] = calculate_average_rr(filtered_trades)
        
        return context


class TradeDetailView(LoginRequiredMixin, DetailView):
    """Detail view for a single trade"""
    model = Trade
    template_name = 'trades/trade_detail.html'
    context_object_name = 'trade'
    login_url = '/admin/login/'
    
    def get_queryset(self):
        return Trade.objects.filter(user=self.request.user)


class TradeCreateView(LoginRequiredMixin, CreateView):
    """Create view for adding new trades"""
    model = Trade
    form_class = TradeForm
    template_name = 'trades/trade_form.html'
    success_url = reverse_lazy('trades:trade_list')
    login_url = '/admin/login/'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Trade {self.object.trade_number} created successfully!'
        )
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class TradeUpdateView(LoginRequiredMixin, UpdateView):
    """Update view for editing existing trades"""
    model = Trade
    form_class = TradeForm
    template_name = 'trades/trade_form.html'
    login_url = '/admin/login/'
    
    def get_queryset(self):
        return Trade.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('trades:trade_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Trade updated successfully!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class TradeDeleteView(LoginRequiredMixin, DeleteView):
    """Delete view with confirmation"""
    model = Trade
    template_name = 'trades/trade_confirm_delete.html'
    success_url = reverse_lazy('trades:trade_list')
    login_url = '/admin/login/'
    
    def get_queryset(self):
        return Trade.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Trade deleted successfully!')
        return super().delete(request, *args, **kwargs)


class StatisticsView(LoginRequiredMixin, TemplateView):
    """Detailed statistics breakdown view"""
    template_name = 'trades/statistics.html'
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_trades = Trade.objects.filter(user=self.request.user)
        closed_trades = user_trades.exclude(outcome='OPEN')
        
        # Overall statistics
        context['total_trades'] = user_trades.count()
        context['total_pnl'] = calculate_pnl(user_trades)
        context['return_percentage'] = calculate_return_percentage(user_trades)
        context['win_rate'] = calculate_win_rate(user_trades)
        context['avg_rr'] = calculate_average_rr(user_trades)
        context['expectancy'] = calculate_expectancy(user_trades)
        
        # Win/Loss counts
        counts = get_win_loss_counts(user_trades)
        context['winners'] = counts['winners']
        context['losers'] = counts['losers']
        context['scratch'] = counts['scratch']
        context['open'] = counts['open']
        
        # By entry type
        context['entry_type_stats'] = get_statistics_by_category(user_trades, 'entry_type')
        
        # By symbol
        context['symbol_stats'] = get_statistics_by_category(user_trades, 'symbol')
        
        # By confidence level
        context['confidence_stats'] = get_statistics_by_category(user_trades, 'confidence_level')
        
        # By direction
        context['direction_stats'] = get_statistics_by_category(user_trades, 'direction')
        
        # Monthly breakdown (last 12 months)
        context['monthly_pnl'] = get_monthly_pnl(self.request.user, 12)
        
        # Best/worst trades and days
        best_worst = get_best_worst_trades(user_trades)
        context['best_trade'] = best_worst['best_trade']
        context['worst_trade'] = best_worst['worst_trade']
        context['best_day'] = best_worst['best_day']
        context['worst_day'] = best_worst['worst_day']
        
        # Current streak
        context['streak'] = get_streak(user_trades)
        
        return context
