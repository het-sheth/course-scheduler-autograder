"""Pre-computed expected output values for PA3 Customer Loan Accounts."""

import math


def compute_monthly_payment(principal: float, annual_rate_pct: float, months: int) -> float:
    """Compute monthly payment using standard loan amortization formula."""
    monthly_rate = (annual_rate_pct / 100.0) / 12.0
    return principal * (monthly_rate / (1 - math.pow(1 + monthly_rate, -months)))


# The exact test data from the PA3 assignment's main method
CAR_LOAN_1 = {
    "principal": 25000.00,
    "rate": 4.9,
    "months": 72,
    "vin": "IRQ3458977",
}
CAR_LOAN_1["payment"] = round(compute_monthly_payment(
    CAR_LOAN_1["principal"], CAR_LOAN_1["rate"], CAR_LOAN_1["months"]), 2)

CAR_LOAN_2 = {
    "principal": 12000.00,
    "rate": 5.0,
    "months": 60,
    "vin": "NXK6767876",
}
CAR_LOAN_2["payment"] = round(compute_monthly_payment(
    CAR_LOAN_2["principal"], CAR_LOAN_2["rate"], CAR_LOAN_2["months"]), 2)

PRIMARY_MORTGAGE_1 = {
    "principal": 250000.00,
    "rate": 3.75,
    "months": 360,
    "pmi": 35.12,
    "street": "321 Main Street",
    "city": "State College",
    "state": "PA",
    "zipcode": "16801",
}
PRIMARY_MORTGAGE_1["payment"] = round(compute_monthly_payment(
    PRIMARY_MORTGAGE_1["principal"], PRIMARY_MORTGAGE_1["rate"], PRIMARY_MORTGAGE_1["months"]), 2)

PRIMARY_MORTGAGE_2 = {
    "principal": 375000.00,
    "rate": 2.5,
    "months": 360,
    "pmi": 53.12,
    "street": "783 Maple Lane",
    "city": "State College",
    "state": "PA",
    "zipcode": "16801",
}
PRIMARY_MORTGAGE_2["payment"] = round(compute_monthly_payment(
    PRIMARY_MORTGAGE_2["principal"], PRIMARY_MORTGAGE_2["rate"], PRIMARY_MORTGAGE_2["months"]), 2)

UNSECURED_LOAN = {
    "principal": 5000.00,
    "rate": 10.75,
    "months": 48,
}
UNSECURED_LOAN["payment"] = round(compute_monthly_payment(
    UNSECURED_LOAN["principal"], UNSECURED_LOAN["rate"], UNSECURED_LOAN["months"]), 2)

# Customers
CUSTOMER_A = {
    "first": "Tony",
    "last": "Stark",
    "ssn": "111-22-3333",
}

CUSTOMER_B = {
    "first": "Gal",
    "last": "Gadot",
    "ssn": "444-55-6666",
}

# All expected payment values for quick lookup
ALL_PAYMENTS = [
    CAR_LOAN_1["payment"],       # 401.46
    CAR_LOAN_2["payment"],       # 226.45
    PRIMARY_MORTGAGE_1["payment"],  # 1157.79
    PRIMARY_MORTGAGE_2["payment"],  # 1481.70
    UNSECURED_LOAN["payment"],   # 128.62
]

TOLERANCE = 0.02


def get_expected_output_text() -> str:
    """Return formatted expected output for the report."""
    return f"""Monthly Report of Customers by Loan Account
Account Report for Customer: {CUSTOMER_A['first']} {CUSTOMER_A['last']} with SSN {CUSTOMER_A['ssn']}

Car Loan with:
Principal: ${CAR_LOAN_1['principal']:.2f}
Annual Interest Rate: {CAR_LOAN_1['rate']:.2f}%
Term of Loan in Months: {CAR_LOAN_1['months']}
Monthly Payment: ${CAR_LOAN_1['payment']:.2f}
Vehicle VIN: {CAR_LOAN_1['vin']}


Primary Mortgage Loan with:
Principal: ${PRIMARY_MORTGAGE_1['principal']:.2f}
Annual Interest Rate: {PRIMARY_MORTGAGE_1['rate']:.2f}%
Term of Loan in Months: {PRIMARY_MORTGAGE_1['months']}
Monthly Payment: ${PRIMARY_MORTGAGE_1['payment']:.2f}
PMI Monthly Amount: ${PRIMARY_MORTGAGE_1['pmi']:.2f}
Property Address:
    {PRIMARY_MORTGAGE_1['street']}
    {PRIMARY_MORTGAGE_1['city']}, {PRIMARY_MORTGAGE_1['state']} {PRIMARY_MORTGAGE_1['zipcode']}


Unsecured Loan with:
Principal: ${UNSECURED_LOAN['principal']:.2f}
Annual Interest Rate: {UNSECURED_LOAN['rate']:.2f}%
Term of Loan in Months: {UNSECURED_LOAN['months']}
Monthly Payment: ${UNSECURED_LOAN['payment']:.2f}



Account Report for Customer: {CUSTOMER_B['first']} {CUSTOMER_B['last']} with SSN {CUSTOMER_B['ssn']}

Car Loan with:
Principal: ${CAR_LOAN_2['principal']:.2f}
Annual Interest Rate: {CAR_LOAN_2['rate']:.2f}%
Term of Loan in Months: {CAR_LOAN_2['months']}
Monthly Payment: ${CAR_LOAN_2['payment']:.2f}
Vehicle VIN: {CAR_LOAN_2['vin']}


Primary Mortgage Loan with:
Principal: ${PRIMARY_MORTGAGE_2['principal']:.2f}
Annual Interest Rate: {PRIMARY_MORTGAGE_2['rate']:.2f}%
Term of Loan in Months: {PRIMARY_MORTGAGE_2['months']}
Monthly Payment: ${PRIMARY_MORTGAGE_2['payment']:.2f}
PMI Monthly Amount: ${PRIMARY_MORTGAGE_2['pmi']:.2f}
Property Address:
    {PRIMARY_MORTGAGE_2['street']}
    {PRIMARY_MORTGAGE_2['city']}, {PRIMARY_MORTGAGE_2['state']} {PRIMARY_MORTGAGE_2['zipcode']}"""
