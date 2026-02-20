"""PA3-specific output verification checks."""

import re
from typing import List

from framework.rubric import RubricItem
from assignments.pa3.expected_values import (
    CAR_LOAN_1, CAR_LOAN_2, PRIMARY_MORTGAGE_1, PRIMARY_MORTGAGE_2,
    UNSECURED_LOAN, CUSTOMER_A, CUSTOMER_B, ALL_PAYMENTS, TOLERANCE
)


def get_item(items: List[RubricItem], item_id: str) -> RubricItem:
    for item in items:
        if item.id == item_id:
            return item
    raise ValueError(f"Rubric item '{item_id}' not found")


def _value_in_output(expected: float, output: str) -> bool:
    """Check if a value appears in output within tolerance."""
    for match in re.finditer(r'\d+\.\d+', output):
        if abs(float(match.group()) - expected) <= TOLERANCE:
            return True
    return False


def check_output(items: List[RubricItem], output: str):
    """Run all output verification checks for PA3."""
    _check_main_code(items, output)
    _check_formatting(items, output)
    _check_decimal_places(items, output)
    _check_numbers(items, output)
    _override_customer_from_output(items, output)


def _check_main_code(items: List[RubricItem], output: str):
    """Check (main_code): output shows customer reports with all loan data."""
    item = get_item(items, "main_code")
    issues = []

    # Check for customer headers
    if CUSTOMER_A["first"] not in output or CUSTOMER_A["last"] not in output:
        issues.append("Customer A (Tony Stark) not found")
    if CUSTOMER_B["first"] not in output or CUSTOMER_B["last"] not in output:
        issues.append("Customer B (Gal Gadot) not found")

    # Check SSNs
    if CUSTOMER_A["ssn"] not in output:
        issues.append("SSN 111-22-3333 not found")
    if CUSTOMER_B["ssn"] not in output:
        issues.append("SSN 444-55-6666 not found")

    # Check for loan type headers
    output_lower = output.lower()
    if "car loan" not in output_lower:
        issues.append("Car Loan section not found")
    if "mortgage" not in output_lower:
        issues.append("Mortgage section not found")
    if "unsecured" not in output_lower:
        issues.append("Unsecured Loan section not found")

    # Check VINs
    if CAR_LOAN_1["vin"] not in output:
        issues.append(f"VIN {CAR_LOAN_1['vin']} not found")
    if CAR_LOAN_2["vin"] not in output:
        issues.append(f"VIN {CAR_LOAN_2['vin']} not found")

    # Check addresses
    if PRIMARY_MORTGAGE_1["street"] not in output:
        issues.append("Address '321 Main Street' not found")
    if PRIMARY_MORTGAGE_2["street"] not in output:
        issues.append("Address '783 Maple Lane' not found")

    if len(issues) >= 5:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "Main method output mostly missing: " + "; ".join(issues)
    elif issues:
        item.deduction = 5
        item.passed = False
        item.notes = "Main method output partially correct: " + "; ".join(issues)


def _check_formatting(items: List[RubricItem], output: str):
    """Check (main_format): $ signs, % signs."""
    item = get_item(items, "main_format")
    issues = []

    if '$' not in output:
        issues.append("no $ symbols found")
    if '%' not in output:
        issues.append("no % symbols found")

    if issues:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "; ".join(issues)


def _check_decimal_places(items: List[RubricItem], output: str):
    """Check (main_decimal): 2 decimal places for dollar amounts."""
    item = get_item(items, "main_decimal")

    # Find all dollar amounts (numbers preceded by $)
    dollar_amounts = re.findall(r'\$(\d+\.\d+)', output)
    bad_format = [n for n in dollar_amounts if len(n.split('.')[1]) != 2]

    if bad_format:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = f"Dollar values not 2 decimal places: {', '.join(bad_format[:3])}"
    elif not dollar_amounts:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "No dollar amounts found in output"


def _check_numbers(items: List[RubricItem], output: str):
    """Check (main_numbers): all payment values match expected output. -2 per wrong value."""
    item = get_item(items, "main_numbers")
    wrong = 0

    # Check all 5 payment values
    payment_checks = [
        (CAR_LOAN_1["payment"], "Car Loan 1 payment"),
        (CAR_LOAN_2["payment"], "Car Loan 2 payment"),
        (PRIMARY_MORTGAGE_1["payment"], "Mortgage 1 payment"),
        (PRIMARY_MORTGAGE_2["payment"], "Mortgage 2 payment"),
        (UNSECURED_LOAN["payment"], "Unsecured Loan payment"),
    ]

    wrong_labels = []
    for expected, label in payment_checks:
        if not _value_in_output(expected, output):
            wrong += 1
            wrong_labels.append(label)

    if wrong > 0:
        deduction = min(wrong * 2, item.max_deduction)
        item.deduction = deduction
        item.passed = False
        item.notes = f"{wrong} payment(s) incorrect: {', '.join(wrong_labels)}"


def _override_customer_from_output(items: List[RubricItem], output: str):
    """Override Customer AST checks if output proves methods work correctly."""
    output_lower = output.lower()

    # If output has "Account Report for Customer:" with correct names and SSNs,
    # then printMonthlyReport works correctly
    cust_item = get_item(items, "cust_printreport")
    if not cust_item.passed:
        has_header_a = bool(re.search(
            r'Account\s+Report\s+for\s+Customer.*Tony\s+Stark.*111-22-3333',
            output, re.IGNORECASE))
        has_header_b = bool(re.search(
            r'Account\s+Report\s+for\s+Customer.*Gal\s+Gadot.*444-55-6666',
            output, re.IGNORECASE))

        # Check that loan data appears under each customer
        has_loans = sum(1 for p in ALL_PAYMENTS if _value_in_output(p, output))

        if has_header_a and has_header_b and has_loans >= 4:
            cust_item.deduction = 0
            cust_item.passed = True
            cust_item.notes = "printMonthlyReport verified via output"
        elif (has_header_a or has_header_b) and has_loans >= 2:
            cust_item.deduction = 7
            cust_item.passed = False
            cust_item.notes = "printMonthlyReport partially correct"

    # If output has correct customer names, addLoanAccount likely works
    addloan_item = get_item(items, "cust_addloan")
    if not addloan_item.passed:
        # If multiple loan types appear with correct payments, addLoanAccount works
        has_loans = sum(1 for p in ALL_PAYMENTS if _value_in_output(p, output))
        if has_loans >= 4:
            addloan_item.deduction = 0
            addloan_item.passed = True
            addloan_item.notes = "addLoanAccount verified via output (loans displayed correctly)"

    # Override getter checks if customer info appears in output
    for getter_id, search_val in [
        ("cust_getter_firstname", [CUSTOMER_A["first"], CUSTOMER_B["first"]]),
        ("cust_getter_lastname", [CUSTOMER_A["last"], CUSTOMER_B["last"]]),
        ("cust_getter_ssn", [CUSTOMER_A["ssn"], CUSTOMER_B["ssn"]]),
    ]:
        getter_item = get_item(items, getter_id)
        if not getter_item.passed:
            # Getters are used in printMonthlyReport header; if both values appear, getter exists
            if all(v in output for v in search_val):
                getter_item.deduction = 0
                getter_item.passed = True
                getter_item.notes = "Getter verified via output"
