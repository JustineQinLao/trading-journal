# Pip Value Calculation Guide

This document explains how pip values and P&L are calculated across different trading platforms and prop firms.

## Overview

The trading journal uses industry-standard calculations that are compatible with:
- **Forex Brokers**: FTMO, MyForexFunds, IC Markets, OANDA, etc.
- **Futures Brokers**: CME Group, NinjaTrader, TradingView
- **Prop Firms**: FTMO, The5ers, FundedNext, MyForexFunds, TopStep

## Calculation Formula

```
P&L (USD) = Pips × Lot Size × Pip Value per Lot
```

---

## 1. FOREX PAIRS

### Standard Pairs (EUR/USD, GBP/USD, AUD/USD, etc.)

**Pip Size**: 0.0001 (4th decimal place)

**Contract Specifications**:
- 1 Standard Lot = 100,000 units
- 1 Mini Lot (0.1) = 10,000 units
- 1 Micro Lot (0.01) = 1,000 units

**Pip Value**:
- 1 Standard Lot: **$10 per pip**
- 0.1 Lot (Mini): **$1 per pip**
- 0.01 Lot (Micro): **$0.10 per pip**

**Example**:
```
Trade: EUR/USD LONG
Entry: 1.1000
Exit: 1.1050
Lot Size: 0.1

Calculation:
- Price Movement: 1.1050 - 1.1000 = 0.0050
- Pips: 0.0050 / 0.0001 = 50 pips
- P&L: 50 pips × 0.1 lot × $10 = $50
```

---

### JPY Pairs (USD/JPY, EUR/JPY, GBP/JPY, etc.)

**Pip Size**: 0.01 (2nd decimal place)

**Contract Specifications**:
- 1 Standard Lot = 100,000 units

**Pip Value**:
- 1 Standard Lot: **$10 per pip** (approximately)
- 0.1 Lot: **$1 per pip**
- 0.01 Lot: **$0.10 per pip**

**Example**:
```
Trade: USD/JPY SHORT
Entry: 150.00
Exit: 149.50
Lot Size: 0.05

Calculation:
- Price Movement: 150.00 - 149.50 = 0.50
- Pips: 0.50 / 0.01 = 50 pips
- P&L: 50 pips × 0.05 lot × $10 = $25
```

---

## 2. METALS

### Gold (XAU/USD)

**Pip Size**: 0.01 (e.g., 1800.00 to 1800.01 = 1 pip)

**Contract Specifications**:
- 1 Standard Lot = 100 troy ounces
- Most brokers use this standard

**Pip Value**:
- 1 Standard Lot: **$1 per pip** (per 0.01 movement)
- 0.1 Lot: **$0.10 per pip**
- 0.01 Lot (Micro): **$0.01 per pip**

**Example**:
```
Trade: XAU/USD LONG
Entry: 1800.00
Exit: 1850.00
Lot Size: 0.1

Calculation:
- Price Movement: 1850.00 - 1800.00 = 50.00
- Pips: 50.00 / 0.01 = 5000 pips
- P&L: 5000 pips × 0.1 lot × $1 = $500
```

**Note**: Some platforms quote gold differently. Always verify with your broker.

---

### Silver (XAG/USD)

**Pip Size**: 0.001 (3rd decimal place)

**Contract Specifications**:
- 1 Standard Lot = 5,000 troy ounces

**Pip Value**:
- 1 Standard Lot: **$5 per pip** (per 0.001 movement)
- 0.1 Lot: **$0.50 per pip**
- 0.01 Lot: **$0.05 per pip**

**Example**:
```
Trade: XAG/USD LONG
Entry: 24.000
Exit: 24.500
Lot Size: 0.1

Calculation:
- Price Movement: 24.500 - 24.000 = 0.500
- Pips: 0.500 / 0.001 = 500 pips
- P&L: 500 pips × 0.1 lot × $5 = $250
```

---

## 3. FUTURES / INDICES

### E-mini Nasdaq-100 (NQ)

**Tick Size**: 0.25 points

**Contract Specifications**:
- Contract Multiplier: $20 per point
- Tick Value: **$5 per tick** (0.25 × $20)

**Example**:
```
Trade: NQ LONG
Entry: 15000.00
Exit: 15010.00
Lot Size: 1 contract

Calculation:
- Price Movement: 15010.00 - 15000.00 = 10 points
- Ticks: 10 / 0.25 = 40 ticks
- P&L: 40 ticks × 1 contract × $5 = $200
```

---

### E-mini S&P 500 (ES)

**Tick Size**: 0.25 points

**Contract Specifications**:
- Contract Multiplier: $50 per point
- Tick Value: **$12.50 per tick** (0.25 × $50)

**Example**:
```
Trade: ES LONG
Entry: 4500.00
Exit: 4505.00
Lot Size: 1 contract

Calculation:
- Price Movement: 4505.00 - 4500.00 = 5 points
- Ticks: 5 / 0.25 = 20 ticks
- P&L: 20 ticks × 1 contract × $12.50 = $250
```

---

### E-mini Dow (YM)

**Tick Size**: 1 point

**Contract Specifications**:
- Contract Multiplier: $5 per point
- Tick Value: **$5 per tick**

**Example**:
```
Trade: YM SHORT
Entry: 35000
Exit: 34990
Lot Size: 1 contract

Calculation:
- Price Movement: 35000 - 34990 = 10 points
- Ticks: 10 / 1 = 10 ticks
- P&L: 10 ticks × 1 contract × $5 = $50
```

---

### E-mini Russell 2000 (RTY)

**Tick Size**: 0.1 points

**Contract Specifications**:
- Contract Multiplier: $50 per point
- Tick Value: **$5 per tick** (0.1 × $50)

**Example**:
```
Trade: RTY LONG
Entry: 2000.0
Exit: 2005.0
Lot Size: 1 contract

Calculation:
- Price Movement: 2005.0 - 2000.0 = 5 points
- Ticks: 5 / 0.1 = 50 ticks
- P&L: 50 ticks × 1 contract × $5 = $250
```

---

## Prop Firm Compatibility

### FTMO
- Uses standard MetaTrader 4/5 pip calculations
- Forex: Standard lot sizing (100,000 units)
- Indices: CFD-based, may vary slightly from futures

### MyForexFunds
- Standard forex pip values apply
- Contract sizes match industry standards

### The5ers / FundedNext / TopStep
- All use industry-standard calculations
- Futures firms use CME contract specifications

---

## Important Notes

1. **Lot Size Input**: 
   - Use decimal notation (e.g., 0.01 for micro lot, 0.1 for mini lot, 1.0 for standard lot)
   - For futures, 1.0 = 1 contract

2. **Currency Conversion**: 
   - All P&L is calculated in USD
   - For non-USD account currencies, apply exchange rate separately

3. **Broker Variations**:
   - Some brokers use 5-digit pricing (pipettes)
   - The system uses standard pip definitions
   - Always verify with your specific broker's contract specifications

4. **Spread & Commission**:
   - Calculations do not include spread or commission
   - Add these costs separately when analyzing trades

---

## Verification

To verify calculations match your platform:

1. **Check Contract Specifications** in your trading platform
2. **Compare Pip Values** using platform's calculator
3. **Test with Small Trade** and verify P&L matches

If you notice discrepancies, check:
- Your broker's specific contract size
- Whether you're trading CFDs vs actual futures
- Account currency (our system uses USD)

---

## References

- CME Group Contract Specifications
- MetaTrader Standard Lot Definitions
- FTMO Trading Conditions
- Industry Standard Forex Calculations

---

*Last Updated: 2025-10-16*
