from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Row, Column, HTML
from crispy_forms.bootstrap import FormActions
from .models import Trade


class TradeForm(forms.ModelForm):
    """Form for creating and editing trades"""
    
    class Meta:
        model = Trade
        fields = [
            'timestamp', 'symbol', 'direction', 'entry_type',
            'entry_price', 'stop_loss', 'take_profit', 'exit_price',
            'lot_size', 'confidence_level', 'outcome', 'screenshot', 'notes'
        ]
        widgets = {
            'timestamp': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                }
            ),
            'entry_price': forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control calc-pips', 'placeholder': 'e.g., 1.08500'}),
            'stop_loss': forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control calc-pips', 'placeholder': 'e.g., 1.08450'}),
            'take_profit': forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control calc-pips', 'placeholder': 'e.g., 1.08700'}),
            'exit_price': forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control', 'placeholder': 'Optional'}),
            'lot_size': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'class': 'form-control', 'placeholder': 'e.g., 0.10'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        
        self.helper.layout = Layout(
            Fieldset(
                'Trade Information',
                Row(
                    Column('timestamp', css_class='form-group col-md-6 mb-3'),
                    Column('symbol', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('direction', css_class='form-group col-md-6 mb-3'),
                    Column('entry_type', css_class='form-group col-md-6 mb-3'),
                ),
            ),
            Fieldset(
                'Price Levels',
                Row(
                    Column('entry_price', css_class='form-group col-md-4 mb-3'),
                    Column('stop_loss', css_class='form-group col-md-4 mb-3'),
                    Column('take_profit', css_class='form-group col-md-4 mb-3'),
                ),
                'exit_price',
                HTML("""
                    <div id="pip-calculator-display" class="mt-3 mb-3 p-3 bg-light rounded" style="display: none;">
                        <h6 class="mb-2">Pip Calculation</h6>
                        <p class="mb-1"><strong>Risk:</strong> <span id="risk-pips-display">-</span> pips</p>
                        <p class="mb-1"><strong>Reward:</strong> <span id="reward-pips-display">-</span> pips</p>
                        <p class="mb-0"><strong>R:R Ratio:</strong> <span id="rr-ratio-display">-</span></p>
                    </div>
                """
                )
            ),
            Fieldset(
                'Position Details',
                Row(
                    Column('lot_size', css_class='form-group col-md-4 mb-3'),
                    Column('confidence_level', css_class='form-group col-md-4 mb-3'),
                    Column('outcome', css_class='form-group col-md-4 mb-3'),

                )
            ),
            Fieldset(
                'Documentation',
                'screenshot',
                'notes',
            ),
            FormActions(
                Submit('submit', 'Save Trade', css_class='btn btn-primary'),
                HTML('<a href="{% url \'trades:trade_list\' %}" class="btn btn-secondary">Cancel</a>')
            )
        )
    
    def clean(self):
        """Custom validation for the form."""
        cleaned_data = super().clean()
        direction = cleaned_data.get('direction')
        entry_price = cleaned_data.get('entry_price')
        stop_loss = cleaned_data.get('stop_loss')
        take_profit = cleaned_data.get('take_profit')

        if not all([direction, entry_price, stop_loss, take_profit]):
            return cleaned_data

        # Validate stop loss placement
        if direction == 'LONG' and stop_loss >= entry_price:
            self.add_error('stop_loss', 'For LONG trades, stop loss must be below entry price.')
        
        if direction == 'SHORT' and stop_loss <= entry_price:
            self.add_error('stop_loss', 'For SHORT trades, stop loss must be above entry price.')

        # Validate take profit placement
        if direction == 'LONG' and take_profit <= entry_price:
            self.add_error('take_profit', 'For LONG trades, take profit must be above entry price.')
        
        if direction == 'SHORT' and take_profit >= entry_price:
            self.add_error('take_profit', 'For SHORT trades, take profit must be below entry price.')

        return cleaned_data


class TradeFilterForm(forms.Form):
    """Form for filtering trades in the list view"""
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='From Date'
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='To Date'
    )
    symbol = forms.ChoiceField(
        required=False,
        choices=[('', 'All Symbols')] + Trade.SYMBOL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    outcome = forms.ChoiceField(
        required=False,
        choices=[('', 'All Outcomes')] + Trade.OUTCOME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    entry_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Entry Types')] + Trade.ENTRY_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Entry Type'
    )
    direction = forms.ChoiceField(
        required=False,
        choices=[('', 'All Directions')] + Trade.DIRECTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Row(
                Column('date_from', css_class='form-group col-md-2 mb-2'),
                Column('date_to', css_class='form-group col-md-2 mb-2'),
                Column('symbol', css_class='form-group col-md-2 mb-2'),
                Column('outcome', css_class='form-group col-md-2 mb-2'),
                Column('entry_type', css_class='form-group col-md-2 mb-2'),
                Column('direction', css_class='form-group col-md-2 mb-2'),
            ),
            FormActions(
                Submit('filter', 'Apply Filters', css_class='btn btn-primary btn-sm'),
                HTML('<a href="{% url \'trades:trade_list\' %}" class="btn btn-secondary btn-sm">Clear</a>')
            )
        )
