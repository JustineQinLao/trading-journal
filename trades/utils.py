from decimal import Decimal
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import timedelta


def calculate_win_rate(queryset):
    """Calculate win rate percentage from a queryset of trades"""
    total = queryset.exclude(outcome='OPEN').count()
    if total == 0:
        return 0
    wins = queryset.filter(outcome='WINNER').count()
    return round((wins / total) * 100, 2)


def calculate_average_rr(queryset):
    """Calculate average risk/reward ratio"""
    avg = queryset.exclude(outcome='OPEN').aggregate(
        avg_rr=Avg('risk_reward_ratio')
    )['avg_rr']
    return round(float(avg or 0), 2)


def calculate_pnl(queryset):
    """Calculate total profit and loss"""
    total = queryset.aggregate(total_pnl=Sum('profit_loss'))['total_pnl']
    return total or Decimal('0')


def calculate_expectancy(queryset):
    """
    Calculate expectancy: (Win Rate × Average Win) - (Loss Rate × Average Loss)
    """
    closed_trades = queryset.exclude(outcome='OPEN')
    total = closed_trades.count()
    
    if total == 0:
        return 0
    
    wins = closed_trades.filter(outcome='WINNER')
    losses = closed_trades.filter(outcome='LOSER')
    
    win_count = wins.count()
    loss_count = losses.count()
    
    if win_count == 0 or loss_count == 0:
        return 0
    
    win_rate = win_count / total
    loss_rate = loss_count / total
    
    avg_win = wins.aggregate(avg=Avg('profit_loss'))['avg'] or 0
    avg_loss = abs(losses.aggregate(avg=Avg('profit_loss'))['avg'] or 0)
    
    expectancy = (win_rate * float(avg_win)) - (loss_rate * float(avg_loss))
    return round(expectancy, 2)


def get_win_loss_counts(queryset):
    """Get counts of wins, losses, and breakevens"""
    counts = queryset.values('outcome').annotate(count=Count('id'))
    result = {
        'winners': 0,
        'losers': 0,
        'scratch': 0,
        'open': 0
    }
    
    for item in counts:
        outcome = item['outcome'].lower()
        if outcome in result:
            result[outcome] = item['count']
    
    return result


def get_best_worst_trades(queryset):
    """Get best and worst trades and days"""
    closed_trades = queryset.exclude(outcome='OPEN')
    
    if not closed_trades.exists():
        return {
            'best_trade': None,
            'worst_trade': None,
            'best_day': None,
            'worst_day': None
        }
    
    best_trade = closed_trades.order_by('-profit_loss').first()
    worst_trade = closed_trades.order_by('profit_loss').first()
    
    # Calculate daily P&L
    from django.db.models.functions import TruncDate
    daily_pnl = closed_trades.annotate(
        date=TruncDate('timestamp')
    ).values('date').annotate(
        daily_pnl=Sum('profit_loss')
    ).order_by('-daily_pnl')
    
    best_day = daily_pnl.first() if daily_pnl else None
    worst_day = daily_pnl.order_by('daily_pnl').first() if daily_pnl else None
    
    return {
        'best_trade': best_trade,
        'worst_trade': worst_trade,
        'best_day': best_day,
        'worst_day': worst_day
    }


def get_streak(queryset):
    """Calculate current winning or losing streak"""
    closed_trades = queryset.exclude(outcome='OPEN').order_by('-timestamp')
    
    if not closed_trades.exists():
        return {'type': None, 'count': 0}
    
    current_outcome = closed_trades.first().outcome
    streak_count = 0
    
    for trade in closed_trades:
        if trade.outcome == current_outcome and current_outcome in ['WINNER', 'LOSER']:
            streak_count += 1
        else:
            break
    
    return {
        'type': current_outcome,
        'count': streak_count
    }


def get_monthly_pnl(user, months=12):
    """Get monthly P&L for the last N months"""
    from trades.models import Trade
    from django.db.models.functions import TruncMonth
    
    end_date = timezone.now()
    start_date = end_date - timedelta(days=months * 30)
    
    monthly_data = Trade.objects.filter(
        user=user,
        timestamp__gte=start_date,
        timestamp__lte=end_date
    ).annotate(
        month=TruncMonth('timestamp')
    ).values('month').annotate(
        total_pnl=Sum('profit_loss'),
        trade_count=Count('id'),
        wins=Count('id', filter=Q(outcome='WINNER')),
        losses=Count('id', filter=Q(outcome='LOSER'))
    ).order_by('month')
    
    return list(monthly_data)


def validate_trade_time(timestamp):
    """Validate that trade timestamp is within allowed hours (9:30-11:00 AM EST)"""
    import pytz
    
    est = pytz.timezone('US/Eastern')
    trade_time_est = timestamp.astimezone(est)
    
    trade_hour = trade_time_est.hour
    trade_minute = trade_time_est.minute
    
    trade_minutes = trade_hour * 60 + trade_minute
    start_minutes = 9 * 60 + 30  # 9:30 AM
    end_minutes = 11 * 60  # 11:00 AM
    
    return start_minutes <= trade_minutes <= end_minutes


def get_statistics_by_category(queryset, category_field):
    """
    Get statistics grouped by a category field (e.g., symbol, entry_type, confidence_level)
    """
    stats = []
    
    categories = queryset.values_list(category_field, flat=True).distinct()
    
    for category in categories:
        category_trades = queryset.filter(**{category_field: category})
        closed_trades = category_trades.exclude(outcome='OPEN')
        
        if closed_trades.exists():
            stats.append({
                'category': category,
                'total_trades': category_trades.count(),
                'winners': closed_trades.filter(outcome='WINNER').count(),
                'losers': closed_trades.filter(outcome='LOSER').count(),
                'win_rate': calculate_win_rate(category_trades),
                'total_pnl': calculate_pnl(category_trades),
                'avg_rr': calculate_average_rr(category_trades),
                'expectancy': calculate_expectancy(category_trades)
            })
    
def calculate_return_percentage(queryset):
    """
    Calculate return percentage: (Total P&L / Total Capital Used) × 100
    """
    total_pnl = calculate_pnl(queryset)
    total_capital = queryset.exclude(capital=0).aggregate(
        total_capital=Sum('capital')
    )['total_capital']

    if total_capital and total_capital > 0:
        return round((float(total_pnl) / float(total_capital)) * 100, 2)
    return 0
