
from tax_rules import OLD_REGIME_SLABS, CESS_RATE

def calculate_tax(income, ded_80c=0, ded_80d=0):
    total_deductions = ded_80c + ded_80d
    taxable_income = max(0, income - total_deductions)

    tax = 0
    prev_limit = 0

    for limit, rate in OLD_REGIME_SLABS:
        if taxable_income > prev_limit:
            taxable_amount = min(limit - prev_limit, taxable_income - prev_limit)
            tax += taxable_amount * rate
            prev_limit = limit
        else:
            break

    cess = tax * CESS_RATE
    total_tax = tax + cess

    return taxable_income, total_tax