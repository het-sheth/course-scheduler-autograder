"""Pre-computed expected output values for PA1 Loan Account."""

import math


def compute_monthly_payment(principal: float, annual_rate_pct: float, num_payments: int) -> float:
    """Compute monthly payment using the standard loan amortization formula."""
    monthly_rate = (annual_rate_pct / 100.0) / 12.0
    return principal * (monthly_rate / (1 - math.pow(1 + monthly_rate, -num_payments)))


# Pre-computed expected values: (rate%, months) -> {"loan1": value, "loan2": value}
EXPECTED = {}
PRINCIPALS = {"loan1": 5000.00, "loan2": 31000.00}
RATES = [1, 5]
TERMS = [(3, 36), (5, 60), (6, 72)]  # (years, months)

for rate in RATES:
    for years, months in TERMS:
        for label, principal in PRINCIPALS.items():
            val = compute_monthly_payment(principal, rate, months)
            EXPECTED[(rate, months, label)] = round(val, 2)

# Convenient lookup: all expected values as formatted strings
EXPECTED_STRINGS = {k: f"{v:.2f}" for k, v in EXPECTED.items()}


def get_expected_output_text() -> str:
    """Return a formatted expected output string for the report."""
    lines = []
    for rate in RATES:
        lines.append(f"Monthly payments at {rate}% interest rate:")
        lines.append("Loan       3 years(36m)  5 years(60m)  6 years(72m)")
        for label, principal in PRINCIPALS.items():
            vals = []
            for _, months in TERMS:
                vals.append(f"${EXPECTED[(rate, months, label)]:.2f}")
            lines.append(f"  {label}(${principal:,.2f})  {'    '.join(vals)}")
        lines.append("")
    return '\n'.join(lines)
