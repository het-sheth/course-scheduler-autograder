"""PA1-specific output verification checks."""

import re
from typing import List

from framework.rubric import RubricItem
from assignments.pa1.expected_values import EXPECTED, EXPECTED_STRINGS, RATES, TERMS, PRINCIPALS

# Tolerance for floating point comparison (covers Math.round differences)
TOLERANCE = 0.02


def get_item(items: List[RubricItem], item_id: str) -> RubricItem:
    for item in items:
        if item.id == item_id:
            return item
    raise ValueError(f"Rubric item '{item_id}' not found")


def _extract_all_numbers(output: str) -> List[float]:
    """Extract all decimal numbers from output as floats."""
    return [float(x) for x in re.findall(r'\d+\.\d+', output)]


def _value_in_output(expected_val: float, output_numbers: List[float]) -> bool:
    """Check if an expected value appears in the output numbers within tolerance."""
    for num in output_numbers:
        if abs(num - expected_val) <= TOLERANCE:
            return True
    return False


def _count_matches(output: str) -> dict:
    """Count how many expected values match in the output, grouped by rate and term."""
    output_numbers = _extract_all_numbers(output)
    matches = {"total": 0, "by_rate": {1: 0, 5: 0}, "by_term": {36: 0, 60: 0, 72: 0}}

    for (rate, months, label), expected_val in EXPECTED.items():
        if _value_in_output(expected_val, output_numbers):
            matches["total"] += 1
            matches["by_rate"][rate] += 1
            matches["by_term"][months] += 1

    return matches


def check_output(items: List[RubricItem], output: str):
    """Run all output verification checks for PA1."""
    matches = _count_matches(output)

    _check_headings(items, output)
    _check_columnar_format(items, output)
    _check_decimal_places(items, output)
    _check_interest_rates(items, output, matches)
    _check_loan_terms(items, output, matches)
    _check_formula_via_output(items, output, matches)
    _check_loan_objects_via_output(items, output, matches)


def _check_headings(items: List[RubricItem], output: str):
    """Check (main_b): heading lines for each interest rate."""
    item = get_item(items, "main_b")

    # Match various ways students might display the rate:
    # "1%", "1 %", "1 percent", "0.01", "rate of 1", "rate: 1"
    has_1pct = bool(re.search(
        r'(?<!\d)1\s*%|1\s*percent|0\.01|rate\s*[:=]?\s*1(?:\s|%|$)',
        output, re.IGNORECASE
    ))
    has_5pct = bool(re.search(
        r'(?<!\d)5\s*%|5\s*percent|0\.05|rate\s*[:=]?\s*5(?:\s|%|$)',
        output, re.IGNORECASE
    ))

    if not has_1pct and not has_5pct:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "No heading lines found for interest rates"
    elif not has_1pct or not has_5pct:
        item.deduction = 3
        item.passed = False
        missing = "1%" if not has_1pct else "5%"
        item.notes = f"Missing heading for {missing} interest rate"


def _check_columnar_format(items: List[RubricItem], output: str):
    """Check (main_c): columnar output format."""
    item = get_item(items, "main_c")
    lines = output.strip().split('\n')

    # Look for lines that contain multiple dollar values (columnar data)
    data_lines = []
    for line in lines:
        nums = re.findall(r'\d+\.\d{2}', line)
        # Filter out principal amounts in headings (5000.00, 31000.00)
        payment_nums = [n for n in nums if float(n) < 5000]
        if len(payment_nums) >= 2:
            data_lines.append(line)

    if len(data_lines) == 0:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "No columnar output detected (no lines with multiple payment values)"
    elif len(data_lines) < 4:
        item.deduction = 5
        item.passed = False
        item.notes = f"Only {len(data_lines)} data lines found, expected at least 4"


def _check_decimal_places(items: List[RubricItem], output: str):
    """Check (main_d): 2 decimal places for all dollar amounts."""
    item = get_item(items, "main_d")

    # Extract numbers that look like payment amounts (not principal amounts in headings)
    all_numbers = re.findall(r'\d+\.\d+', output)

    # Filter to only payment-range values (roughly 50-1000)
    payment_numbers = []
    for num_str in all_numbers:
        val = float(num_str)
        if 50 <= val <= 1000:
            payment_numbers.append(num_str)

    if not payment_numbers:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "No payment values found in output"
        return

    bad_format = []
    for num_str in payment_numbers:
        decimal_part = num_str.split('.')[1]
        if len(decimal_part) != 2:
            bad_format.append(num_str)

    if bad_format:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = f"Values not formatted to 2 decimal places: {', '.join(bad_format[:3])}"


def _check_interest_rates(items: List[RubricItem], output: str, matches: dict):
    """Check (main_e): displays info at 1% and 5% interest rates."""
    item = get_item(items, "main_e")

    rate_1_found = matches["by_rate"][1]
    rate_5_found = matches["by_rate"][5]

    if rate_1_found == 0 and rate_5_found == 0:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "No expected payment values found for either interest rate"
    elif rate_1_found == 0:
        item.deduction = 5
        item.passed = False
        item.notes = "Payment values for 1% interest rate not found in output"
    elif rate_5_found == 0:
        item.deduction = 5
        item.passed = False
        item.notes = "Payment values for 5% interest rate not found in output"


def _check_loan_terms(items: List[RubricItem], output: str, matches: dict):
    """Check (main_f): displays payment amounts for 3, 5, and 6 year loans."""
    item = get_item(items, "main_f")

    terms_found = {m: matches["by_term"][m] > 0 for m in [36, 60, 72]}
    missing_terms = [m for m, found in terms_found.items() if not found]

    if len(missing_terms) == 3:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "No expected payment values found for any loan term"
    elif missing_terms:
        term_names = {36: "3-year", 60: "5-year", 72: "6-year"}
        missing = [term_names[m] for m in missing_terms]
        item.deduction = (len(missing_terms) * item.max_deduction) // 3
        item.passed = False
        item.notes = f"Missing payment values for: {', '.join(missing)}"


def _check_formula_via_output(items: List[RubricItem], output: str, matches: dict):
    """
    Check (class_d_i): verify formula correctness by comparing output values.
    If expected values appear in output (with tolerance), formula is correct.
    This overrides the AST-only Math.pow check.
    """
    item = get_item(items, "class_d_i")
    total_expected = len(EXPECTED)

    if matches["total"] == total_expected:
        item.deduction = 0
        item.passed = True
        item.notes = "Formula verified: all output values match expected"
    elif matches["total"] > total_expected // 2:
        item.deduction = 0
        item.passed = True
        item.notes = f"Formula mostly correct: {matches['total']}/{total_expected} values match"
    elif matches["total"] > 0:
        item.deduction = 5
        item.passed = False
        item.notes = f"Formula partially correct: only {matches['total']}/{total_expected} values match"
    # If matches["total"] == 0, keep whatever was set by the AST check


def _check_loan_objects_via_output(items: List[RubricItem], output: str, matches: dict):
    """
    Override loan object AST check if output proves objects were created correctly.
    If we see correct values for both loan1 and loan2, the objects exist.
    """
    item = get_item(items, "main_a")

    if not item.passed and matches["total"] >= 8:
        # At least 8 out of 12 values match - both loans are clearly working
        item.deduction = 0
        item.passed = True
        item.notes = "Loan objects verified via output (correct payment values present)"
