from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import Trade, AccountBalance


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    """Admin interface for Trade model"""
    
    list_display = [
        'trade_number', 'timestamp', 'user', 'symbol', 'direction', 
        'entry_type', 'outcome', 'profit_loss', 'pnl_pips', 'capital', 'risk_reward_ratio'
    ]
    
    list_filter = [
        'outcome', 'symbol', 'direction', 'entry_type', 
        'confidence_level', 'timestamp'
    ]
    
    search_fields = ['trade_number', 'notes', 'user__username']
    
    readonly_fields = [
        'trade_number', 'profit_loss', 'risk_reward_ratio', 'outcome', 
        'risk_pips', 'reward_pips', 'pnl_pips',
        'created_at', 'updated_at'
    ]
    
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Identification', {
            'fields': ('user', 'trade_number', 'timestamp', 'symbol')
        }),
        ('Strategy', {
            'fields': ('direction', 'entry_type', 'timeframe_analysis', 'confidence_level')
        }),
        ('Price Levels', {
            'fields': ('entry_price', 'stop_loss', 'take_profit', 'exit_price')
        }),
        ('Position', {
            'fields': ('lot_size', 'capital')
        }),
        ('Results (Auto-calculated)', {
            'fields': ('outcome', 'profit_loss', 'pnl_pips', 'risk_pips', 'reward_pips', 'risk_reward_ratio'),
            'classes': ('collapse',)
        }),
        ('Documentation', {
            'fields': ('screenshot', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['export_to_csv']
    
    def export_to_csv(self, request, queryset):
        """Export selected trades to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="trades_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Trade Number', 'Timestamp', 'User', 'Symbol', 'Direction', 'Entry Type', 
            'Entry Price', 'Stop Loss', 'Take Profit', 'Exit Price', 'Lot Size', 'Capital',
            'Confidence', 'Outcome', 'P&L (USD)', 'P&L (Pips)', 'Risk (Pips)', 
            'Reward (Pips)', 'R:R Ratio', 'Notes'
        ])
        
        for trade in queryset:
            writer.writerow([
                trade.trade_number,
                trade.timestamp,
                trade.user.username,
                trade.symbol,
                trade.direction,
                trade.entry_type,
                trade.entry_price,
                trade.stop_loss,
                trade.take_profit,
                trade.exit_price or '',
                trade.lot_size,
                trade.capital,
                trade.confidence_level,
                trade.outcome,
                trade.profit_loss,
                trade.pnl_pips,
                trade.risk_pips,
                trade.reward_pips,
                trade.risk_reward_ratio,
                trade.notes
            ])
        
        return response
    
    export_to_csv.short_description = "Export selected trades to CSV"


@admin.register(AccountBalance)
class AccountBalanceAdmin(admin.ModelAdmin):
    """Admin interface for AccountBalance model"""
    
    list_display = ['user', 'balance', 'initial_balance', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Balance Information', {
            'fields': ('initial_balance', 'balance')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['recalculate_balances', 'reset_balances']
    
    def recalculate_balances(self, request, queryset):
        """Recalculate balances from trades"""
        for account in queryset:
            account.recalculate_balance()
        self.message_user(request, f"Recalculated {queryset.count()} account balances.")
    
    recalculate_balances.short_description = "Recalculate selected account balances"
    
    def reset_balances(self, request, queryset):
        """Reset balances to initial balance"""
        for account in queryset:
            account.reset_balance()
        self.message_user(request, f"Reset {queryset.count()} account balances to initial balance.")
    
    reset_balances.short_description = "Reset selected balances to initial balance"
