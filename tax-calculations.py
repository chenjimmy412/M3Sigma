def after_tax_income(gross_income):
    if not (48000 <= gross_income <= 142000):
        raise ValueError("Income must be between $48,000 and $142,000")

    # 2026 standard deduction (single filer)
    standard_deduction = 16100 
    taxable_income = max(0, gross_income - standard_deduction)

    # Federal income tax brackets (single filer, 2024)
    brackets = [
        (11925, 0.10),
        (48475, 0.12),
        (103350, 0.22),
        (197300, 0.24), 
        (250525, 0.32), 
(626350, 0.35)  
    ]

    federal_tax = 0
    prev_limit = 0

    for limit, rate in brackets:
        if taxable_income > limit:
            federal_tax += (limit - prev_limit) * rate
            prev_limit = limit
        else:
            federal_tax += (taxable_income - prev_limit) * rate
            break

    # Payroll taxes
    social_security = 0.062 * gross_income
    medicare = 0.0145 * gross_income

    total_tax = federal_tax + social_security + medicare
    net_income = gross_income - total_tax

    return round(net_income, 2)


if __name__ == "__main__":
    gross_values = [48514, 102494, 128285, 141121, 121571, 75460, 56028]
    print(f"{'Gross':>12} {'Tax':>12} {'Net':>12}")
    print("-" * 38)
    for g in gross_values:
        net = after_tax_income(g)
        tax = g - net
        print(f"${g:>10,} ${tax:>10,.2f} ${net:>10,.2f}")
