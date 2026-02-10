"""PA2-specific output verification checks."""

import re
from typing import List

from framework.rubric import RubricItem
from assignments.pa2.expected_values import (
    CAR_LOAN, PRIMARY_MORTGAGE, UNSECURED_LOAN, TOLERANCE
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
    """Run all output verification checks for PA2."""
    _check_main_code(items, output)
    _check_formatting(items, output)
    _override_tostring_from_output(items, output)
    _override_calculate_from_output(items, output)


def _check_main_code(items: List[RubricItem], output: str):
    """Check (main_code): output shows all three loan types with correct data."""
    item = get_item(items, "main_code")
    issues = []

    # Check car loan data
    if not _value_in_output(CAR_LOAN["payment"], output):
        issues.append("car loan payment not found")
    if CAR_LOAN["vin"] not in output:
        issues.append("VIN not found")

    # Check mortgage data
    if not _value_in_output(PRIMARY_MORTGAGE["payment"], output):
        issues.append("mortgage payment not found")
    if not _value_in_output(PRIMARY_MORTGAGE["pmi"], output):
        issues.append("PMI amount not found")
    if PRIMARY_MORTGAGE["street"] not in output and "321" not in output:
        issues.append("property address not found")

    # Check unsecured loan data
    if not _value_in_output(UNSECURED_LOAN["payment"], output):
        issues.append("unsecured loan payment not found")

    if len(issues) >= 4:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "Main method output mostly missing: " + "; ".join(issues)
    elif issues:
        item.deduction = 5
        item.passed = False
        item.notes = "Main method output partially correct: " + "; ".join(issues)


def _check_formatting(items: List[RubricItem], output: str):
    """Check (main_format): $ signs, % signs, 2 decimal places."""
    item = get_item(items, "main_format")
    issues = []

    # Check for $ in output
    if '$' not in output:
        issues.append("no $ symbols found")

    # Check for % in output
    if '%' not in output:
        issues.append("no % symbols found")

    # Check decimal places on payment-range values
    all_numbers = re.findall(r'\d+\.\d+', output)
    payment_numbers = [n for n in all_numbers if 30 <= float(n) <= 300000]
    bad_format = [n for n in payment_numbers if len(n.split('.')[1]) != 2]
    if bad_format:
        issues.append(f"values not 2 decimal places: {', '.join(bad_format[:3])}")

    if issues:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "; ".join(issues)


def _override_tostring_from_output(items: List[RubricItem], output: str):
    """Override toString AST checks if output proves they work."""
    output_lower = output.lower()

    # LoanAccount toString - check for principal/rate/months display
    la_item = get_item(items, "la_tostring")
    if not la_item.passed:
        has_principal = bool(re.search(r'principal.*\$?\d+', output, re.IGNORECASE))
        has_rate = bool(re.search(r'(?:interest|rate).*\d+\.\d+\s*%', output, re.IGNORECASE))
        has_months = bool(re.search(r'(?:month|term).*\d+', output, re.IGNORECASE))
        if has_principal and has_rate and has_months:
            la_item.deduction = 0
            la_item.passed = True
            la_item.notes = "toString verified via output"

    # CarLoan toString - check for VIN display
    cl_item = get_item(items, "cl_tostring")
    if not cl_item.passed:
        if "car loan" in output_lower and CAR_LOAN["vin"] in output:
            cl_item.deduction = 0
            cl_item.passed = True
            cl_item.notes = "toString verified via output (VIN present)"

    # PrimaryMortgage toString - check for PMI and address
    pm_item = get_item(items, "pm_tostring")
    if not pm_item.passed:
        has_pmi = bool(re.search(r'pmi|mortgage\s+insurance', output_lower))
        has_addr = PRIMARY_MORTGAGE["street"] in output or "321 main" in output_lower
        if "mortgage" in output_lower:
            if has_pmi and has_addr:
                pm_item.deduction = 0
                pm_item.passed = True
                pm_item.notes = "toString verified via output"
            elif has_pmi or has_addr:
                pm_item.deduction = 5
                pm_item.passed = False
                pm_item.notes = "toString partially correct: missing " + \
                                ("address" if not has_addr else "PMI info")

    # UnsecuredLoan toString
    ul_item = get_item(items, "ul_tostring")
    if not ul_item.passed:
        if "unsecured" in output_lower and _value_in_output(UNSECURED_LOAN["payment"], output):
            ul_item.deduction = 0
            ul_item.passed = True
            ul_item.notes = "toString verified via output"

    # Address toString
    addr_item = get_item(items, "addr_tostring")
    if not addr_item.passed:
        has_street = PRIMARY_MORTGAGE["street"] in output
        has_city = PRIMARY_MORTGAGE["city"] in output
        has_state = PRIMARY_MORTGAGE["state"] in output
        has_zip = PRIMARY_MORTGAGE["zipcode"] in output
        found = sum([has_street, has_city, has_state, has_zip])
        if found >= 3:
            addr_item.deduction = 0
            addr_item.passed = True
            addr_item.notes = "toString verified via output"
        elif found >= 1:
            addr_item.deduction = 5
            addr_item.passed = False
            addr_item.notes = f"Address toString partial: {found}/4 parts found"


def _override_calculate_from_output(items: List[RubricItem], output: str):
    """Override calculateMonthlyPayment check if output has correct values."""
    item = get_item(items, "la_calculate")

    payments_found = 0
    if _value_in_output(CAR_LOAN["payment"], output):
        payments_found += 1
    if _value_in_output(PRIMARY_MORTGAGE["payment"], output):
        payments_found += 1
    if _value_in_output(UNSECURED_LOAN["payment"], output):
        payments_found += 1

    if payments_found == 3:
        item.deduction = 0
        item.passed = True
        item.notes = "Formula verified: all payment values correct"
    elif payments_found >= 2 and not item.passed:
        item.deduction = 3
        item.passed = False
        item.notes = f"Formula partially correct: {payments_found}/3 payments match"
