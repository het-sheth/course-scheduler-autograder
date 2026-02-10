"""Pre-computed expected output values for PA2 Loan Account Hierarchy."""

import math


def compute_monthly_payment(principal: float, annual_rate_pct: float, months: int) -> float:
    """Compute monthly payment using standard loan amortization formula."""
    monthly_rate = (annual_rate_pct / 100.0) / 12.0
    return principal * (monthly_rate / (1 - math.pow(1 + monthly_rate, -months)))


# The exact test data from the assignment's main method
CAR_LOAN = {
    "principal": 25000.00,
    "rate": 4.25,
    "months": 72,
    "vin": "IRQ3458977",
}
CAR_LOAN["payment"] = round(compute_monthly_payment(
    CAR_LOAN["principal"], CAR_LOAN["rate"], CAR_LOAN["months"]), 2)

PRIMARY_MORTGAGE = {
    "principal": 250000.00,
    "rate": 3.1,
    "months": 360,
    "pmi": 35.12,
    "street": "321 Main Street",
    "city": "State College",
    "state": "PA",
    "zipcode": "16801",
}
PRIMARY_MORTGAGE["payment"] = round(compute_monthly_payment(
    PRIMARY_MORTGAGE["principal"], PRIMARY_MORTGAGE["rate"], PRIMARY_MORTGAGE["months"]), 2)

UNSECURED_LOAN = {
    "principal": 5000.00,
    "rate": 10.75,
    "months": 48,
}
UNSECURED_LOAN["payment"] = round(compute_monthly_payment(
    UNSECURED_LOAN["principal"], UNSECURED_LOAN["rate"], UNSECURED_LOAN["months"]), 2)

EXPECTED_PAYMENTS = {
    "car": CAR_LOAN["payment"],        # 393.98
    "mortgage": PRIMARY_MORTGAGE["payment"],  # 1067.54
    "unsecured": UNSECURED_LOAN["payment"],   # 128.62
}

TOLERANCE = 0.02


def get_expected_output_text() -> str:
    """Return formatted expected output for the report."""
    return f"""Car Loan with:
Principal: ${CAR_LOAN['principal']:.2f}
Annual Interest Rate: {CAR_LOAN['rate']:.2f}%
Term of Loan in Months: {CAR_LOAN['months']}
Monthly Payment: ${CAR_LOAN['payment']:.2f}
Vehicle VIN: {CAR_LOAN['vin']}

Primary Mortgage Loan with:
Principal: ${PRIMARY_MORTGAGE['principal']:.2f}
Annual Interest Rate: {PRIMARY_MORTGAGE['rate']:.2f}%
Term of Loan in Months: {PRIMARY_MORTGAGE['months']}
Monthly Payment: ${PRIMARY_MORTGAGE['payment']:.2f}
PMI Monthly Amount: ${PRIMARY_MORTGAGE['pmi']:.2f}
Property Address:
    {PRIMARY_MORTGAGE['street']}
    {PRIMARY_MORTGAGE['city']}, {PRIMARY_MORTGAGE['state']} {PRIMARY_MORTGAGE['zipcode']}

Unsecured Loan with:
Principal: ${UNSECURED_LOAN['principal']:.2f}
Annual Interest Rate: {UNSECURED_LOAN['rate']:.2f}%
Term of Loan in Months: {UNSECURED_LOAN['months']}
Monthly Payment: ${UNSECURED_LOAN['payment']:.2f}"""
