from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal
import pytz


class AccountBalance(models.Model):
    """Model to track user's account balance"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account_balance')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('100.00'))
    initial_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('100.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Account Balance'
        verbose_name_plural = 'Account Balances'
    
    def __str__(self):
        return f"{self.user.username} - Balance: ${self.balance}"
    
    def reset_balance(self):
        """Reset balance to initial balance"""
        self.balance = self.initial_balance
        self.save()
    
    def recalculate_balance(self):
        """Recalculate balance from all closed trades"""
        from django.db.models import Sum
        total_pnl = Trade.objects.filter(
            user=self.user,
            outcome__in=['WINNER', 'LOSER', 'SCRATCH']
        ).aggregate(Sum('profit_loss'))['profit_loss__sum'] or Decimal('0')
        
        self.balance = self.initial_balance + total_pnl
        self.save()


class Trade(models.Model):
    """Model representing a single trade entry for ICT strategy"""
    
    # Choices for dropdown fields
    SYMBOL_CHOICES = [
        # Indices
        ('NQ', 'NQ - Nasdaq'),
        ('ES', 'ES - S&P 500'),
        ('YM', 'YM - Dow Jones'),
        ('RTY', 'RTY - Russell 2000'),
        # Forex majors
        ('EURUSD', 'EUR/USD'),
        ('GBPUSD', 'GBP/USD'),
        ('USDJPY', 'USD/JPY'),
        ('USDCHF', 'USD/CHF'),
        ('AUDUSD', 'AUD/USD'),
        ('NZDUSD', 'NZD/USD'),
        ('USDCAD', 'USD/CAD'),
        # Metals
        ('XAUUSD', 'XAU/USD (Gold)'),
        ('XAGUSD', 'XAG/USD (Silver)'),
    ]
    
    DIRECTION_CHOICES = [
        ('LONG', 'Long'),
        ('SHORT', 'Short'),
    ]
    
    ENTRY_TYPE_CHOICES = [
        ('CONFIRMATION', 'Confirmation'),
        ('FAIL_FLIP', 'Fail Flip'),
    ]
    
    CONFIDENCE_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]
    
    OUTCOME_CHOICES = [
        ('WINNER', 'Winner'),
        ('LOSER', 'Loser'),
        ('SCRATCH', 'Scratch'),
        ('OPEN', 'Open')
    ]
    
    # 1. Identification
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trades')
    trade_number = models.CharField(max_length=20, unique=True, editable=False)
    timestamp = models.DateTimeField(help_text="When the trade was taken")
    symbol = models.CharField(max_length=10, choices=SYMBOL_CHOICES)
    
    # 2. Strategy
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE_CHOICES)
    timeframe_analysis = models.CharField(
        max_length=50, 
        default='1D → 1H → 5M',
        help_text="Timeframe analysis used"
    )
    
    # 3. Price Levels (User Input)
    entry_price = models.DecimalField(max_digits=12, decimal_places=5, help_text="Entry price")
    stop_loss = models.DecimalField(max_digits=12, decimal_places=5, help_text="Stop loss price")
    take_profit = models.DecimalField(max_digits=12, decimal_places=5, help_text="Take profit price")
    exit_price = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True, help_text="Exit price")

    # 4. Position
    lot_size = models.DecimalField(max_digits=5, decimal_places=2, help_text="Position size in lots (e.g., 0.01, 1.0)")
    capital = models.DecimalField(max_digits=12, decimal_places=2, help_text="Account capital/balance at time of trade (USD)")
    confidence_level = models.CharField(max_length=10, choices=CONFIDENCE_CHOICES)

    # 5. Results (auto-calculated)
    outcome = models.CharField(max_length=10, choices=OUTCOME_CHOICES, default='OPEN')
    profit_loss = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, help_text="P&L in USD")
    risk_pips = models.DecimalField(max_digits=10, decimal_places=1, default=0, editable=False, help_text="Risk in pips")
    reward_pips = models.DecimalField(max_digits=10, decimal_places=1, default=0, editable=False, help_text="Reward in pips")
    pnl_pips = models.DecimalField(max_digits=10, decimal_places=1, default=0, editable=False, help_text="P&L in pips")
    risk_reward_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False)
    
    # 6. Documentation
    screenshot = models.ImageField(
        upload_to='trade_screenshots/', 
        null=True, 
        blank=True,
        help_text="Optional screenshot of the trade setup"
    )
    notes = models.TextField(blank=True, help_text="Additional notes about the trade")
    
    # 7. Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Trade'
        verbose_name_plural = 'Trades'
    
    def __str__(self):
        return f"{self.trade_number} - {self.symbol} {self.direction} - {self.outcome}"
    
    def _get_pip_size(self):
        """Return the pip size for the symbol."""
        if 'JPY' in self.symbol:
            return Decimal('0.01')  # JPY pairs: 2nd decimal
        elif self.symbol == 'XAUUSD':
            return Decimal('0.01')  # Gold: 0.01 (e.g., 1800.00 to 1800.01 = 1 pip)
        elif self.symbol == 'XAGUSD':
            return Decimal('0.001')  # Silver: 0.001 (more granular)
        elif self.symbol in ['NQ', 'ES', 'YM', 'RTY']:
            return Decimal('0.25')  # Futures use tick size, not pips
        else:  # Standard Forex pairs
            return Decimal('0.0001')  # 4th decimal
    
    def _get_pip_value_per_lot(self):
        """
        Return the pip value per 1.0 lot for the symbol.
        This varies by instrument type and follows industry standards.
        
        Standard Forex (1 lot = 100,000 units):
        - Standard pairs: $10 per pip per lot
        - JPY pairs: $10 per pip per lot (adjusted for pip size)
        
        Metals (1 lot = 100 oz for Gold, 5000 oz for Silver):
        - XAUUSD: $1 per 0.01 pip per lot (100 oz)
        - XAGUSD: $5 per 0.001 pip per lot (5000 oz)
        
        Futures (contract-based):
        - NQ: $5 per 0.25 tick (E-mini Nasdaq = $20 per point)
        - ES: $12.50 per 0.25 tick (E-mini S&P = $50 per point)
        - YM: $5 per 1 tick (E-mini Dow)
        - RTY: $5 per 0.1 tick (E-mini Russell = $50 per point)
        """
        if self.symbol in ['NQ']:
            # NQ: $20 per point, 0.25 tick = $5 per tick
            return Decimal('5.0')
        elif self.symbol in ['ES']:
            # ES: $50 per point, 0.25 tick = $12.50 per tick
            return Decimal('12.5')
        elif self.symbol in ['YM']:
            # YM: $5 per point, 1 tick = $5 per tick
            return Decimal('5.0')
        elif self.symbol in ['RTY']:
            # RTY: $50 per point, 0.1 tick = $5 per tick
            return Decimal('5.0')
        elif self.symbol == 'XAUUSD':
            # Gold: 1 lot = 100 oz, 1 pip (0.01) = $1
            # So per 0.01 lot (micro): $0.01, per 1.0 lot: $1
            return Decimal('1.0')
        elif self.symbol == 'XAGUSD':
            # Silver: 1 lot = 5000 oz, 1 pip (0.001) = $5
            return Decimal('5.0')
        elif 'JPY' in self.symbol:
            # JPY pairs: 1 pip (0.01) = $10 per lot (adjusted)
            # Contract size = 100,000, pip = 0.01
            # Value = 100,000 * 0.01 / current rate ≈ $10
            return Decimal('10.0')
        else:
            # Standard Forex pairs: 1 pip (0.0001) = $10 per lot
            # Contract size = 100,000, pip = 0.0001
            # Value = 100,000 * 0.0001 = $10
            return Decimal('10.0')

    def save(self, *args, **kwargs):
        """Override save to auto-generate trade number and calculate all result fields."""
        # 1. Generate trade_number if it's a new trade
        if not self.trade_number:
            today = timezone.now().date()
            date_prefix = today.strftime('%Y%m%d')
            today_trades = Trade.objects.filter(trade_number__startswith=date_prefix).count()
            self.trade_number = f"{date_prefix}-{today_trades + 1:03d}"

        # 2. Calculate Risk and Reward in Pips
        pip_size = self._get_pip_size()
        risk_price = abs(self.entry_price - self.stop_loss)
        reward_price = abs(self.take_profit - self.entry_price)
        
        self.risk_pips = risk_price / pip_size
        self.reward_pips = reward_price / pip_size

        # 3. Calculate Risk-Reward Ratio
        if self.risk_pips > 0:
            self.risk_reward_ratio = round(self.reward_pips / self.risk_pips, 2)
        else:
            self.risk_reward_ratio = 0

        # 4. Calculate P&L and Outcome based on exit_price or manual outcome
        if self.exit_price is not None:
            # Exit price is set - calculate P&L and determine outcome
            pnl_price = self.exit_price - self.entry_price if self.direction == 'LONG' else self.entry_price - self.exit_price
            self.pnl_pips = pnl_price / pip_size
            
            # Calculate P&L in USD based on instrument type
            pip_value_per_lot = self._get_pip_value_per_lot()
            self.profit_loss = self.pnl_pips * self.lot_size * pip_value_per_lot

            # Auto-determine outcome based on P&L
            if self.profit_loss > 0:
                self.outcome = 'WINNER'
            elif self.profit_loss < 0:
                self.outcome = 'LOSER'
            else:
                self.outcome = 'SCRATCH'
        elif self.outcome in ['WINNER', 'LOSER', 'SCRATCH']:
            # Manual outcome set without exit_price - calculate based on outcome
            # Assume trade hit TP for WINNER, SL for LOSER, or entry for SCRATCH
            if self.outcome == 'WINNER':
                # Assume hit take profit
                pnl_price = self.take_profit - self.entry_price if self.direction == 'LONG' else self.entry_price - self.take_profit
                self.pnl_pips = pnl_price / pip_size
                pip_value_per_lot = self._get_pip_value_per_lot()
                self.profit_loss = self.pnl_pips * self.lot_size * pip_value_per_lot
            elif self.outcome == 'LOSER':
                # Assume hit stop loss
                pnl_price = self.stop_loss - self.entry_price if self.direction == 'LONG' else self.entry_price - self.stop_loss
                self.pnl_pips = pnl_price / pip_size
                pip_value_per_lot = self._get_pip_value_per_lot()
                self.profit_loss = self.pnl_pips * self.lot_size * pip_value_per_lot
            else:  # SCRATCH
                self.pnl_pips = Decimal('0')
                self.profit_loss = Decimal('0')
        else:
            # Trade is OPEN - reset P&L fields
            self.profit_loss = Decimal('0')
            self.pnl_pips = Decimal('0')

        super().save(*args, **kwargs)
    
    def validate_entry_time(self):
        """Optional validation - can be disabled for flexible entry"""
        # Time validation removed to allow trades at any time
        return True
    
    def clean(self):
        """Validate the model data before saving."""
        super().clean()

        # Validate stop loss placement - only if all required fields are present
        if all([self.direction, self.entry_price, self.stop_loss, self.take_profit]):
            # Validate stop loss placement
            if self.direction == 'LONG' and self.stop_loss >= self.entry_price:
                raise ValidationError({'stop_loss': 'For LONG trades, stop loss must be below entry price.'})

            if self.direction == 'SHORT' and self.stop_loss <= self.entry_price:
                raise ValidationError({'stop_loss': 'For SHORT trades, stop loss must be above entry price.'})

            # Validate take profit placement
            if self.direction == 'LONG' and self.take_profit <= self.entry_price:
                raise ValidationError({'take_profit': 'For LONG trades, take profit must be above entry price.'})

            if self.direction == 'SHORT' and self.take_profit >= self.entry_price:
                raise ValidationError({'take_profit': 'For SHORT trades, take profit must be below entry price.'})


# Signal handlers to update account balance when trades are saved or deleted
@receiver(post_save, sender=Trade)
def update_balance_on_trade_save(sender, instance, created, **kwargs):
    """Update account balance when a trade is saved"""
    # Get or create account balance for the user
    account_balance, created_balance = AccountBalance.objects.get_or_create(
        user=instance.user,
        defaults={'balance': Decimal('100.00'), 'initial_balance': Decimal('100.00')}
    )
    
    # Recalculate balance from all closed trades
    account_balance.recalculate_balance()


@receiver(post_delete, sender=Trade)
def update_balance_on_trade_delete(sender, instance, **kwargs):
    """Update account balance when a trade is deleted"""
    try:
        account_balance = AccountBalance.objects.get(user=instance.user)
        account_balance.recalculate_balance()
    except AccountBalance.DoesNotExist:
        pass


@receiver(post_save, sender=User)
def create_account_balance(sender, instance, created, **kwargs):
    """Create account balance when a new user is created"""
    if created:
        AccountBalance.objects.create(
            user=instance,
            balance=Decimal('100.00'),
            initial_balance=Decimal('100.00')
        )
