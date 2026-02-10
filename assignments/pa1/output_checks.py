"""PA1-specific output verification checks."""

import re
from typing import List

from framework.rubric import RubricItem
from assignments.pa1.expected_values import EXPECTED, EXPECTED_STRINGS, RATES, TERMS, PRINCIPALS


def get_item(items: List[RubricItem], item_id: str) -> RubricItem:
    for item in items:
        if item.id == item_id:
            return item
    raise ValueError(f"Rubric item '{item_id}' not found")


def check_output(items: List[RubricItem], output: str):
    """Run all output verification checks for PA1."""
    _check_headings(items, output)
    _check_columnar_format(items, output)
    _check_decimal_places(items, output)
    _check_interest_rates(items, output)
    _check_loan_terms(items, output)
    _check_formula_via_output(items, output)


def _extract_numbers(output: str) -> List[str]:
    """Extract all decimal numbers from output."""
    return re.findall(r'\d+\.\d+', output)


def _check_headings(items: List[RubricItem], output: str):
    """Check (main_b): heading lines for each interest rate."""
    item = get_item(items, "main_b")

    has_1pct_heading = bool(re.search(r'1\s*%|1\s*percent', output, re.IGNORECASE))
    has_5pct_heading = bool(re.search(r'5\s*%|5\s*percent', output, re.IGNORECASE))

    if not has_1pct_heading and not has_5pct_heading:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "No heading lines found for interest rates"
    elif not has_1pct_heading or not has_5pct_heading:
        item.deduction = 3
        item.passed = False
        missing = "1%" if not has_1pct_heading else "5%"
        item.notes = f"Missing heading for {missing} interest rate"


def _check_columnar_format(items: List[RubricItem], output: str):
    """Check (main_c): columnar output format."""
    item = get_item(items, "main_c")
    lines = output.strip().split('\n')

    # Look for lines that contain multiple dollar values (columnar data)
    data_lines = []
    for line in lines:
        nums = re.findall(r'\d+\.\d{2}', line)
        if len(nums) >= 2:
            data_lines.append(line)

    if len(data_lines) == 0:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "No columnar output detected (no lines with multiple values)"
    elif len(data_lines) < 4:
        # Expect at least 4 data lines (2 loans * 2 rates, or 2 rates * some lines)
        item.deduction = 5
        item.passed = False
        item.notes = f"Only {len(data_lines)} data lines found, expected at least 4"


def _check_decimal_places(items: List[RubricItem], output: str):
    """Check (main_d): 2 decimal places for all dollar amounts."""
    item = get_item(items, "main_d")
    numbers = _extract_numbers(output)

    if not numbers:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "No numeric values found in output"
        return

    bad_format = []
    for num_str in numbers:
        decimal_part = num_str.split('.')[1]
        if len(decimal_part) != 2:
            bad_format.append(num_str)

    if bad_format:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = f"Values not formatted to 2 decimal places: {', '.join(bad_format[:3])}"


def _check_interest_rates(items: List[RubricItem], output: str):
    """Check (main_e): displays info at 1% and 5% interest rates."""
    item = get_item(items, "main_e")

    # Check if expected values for both rates appear in output
    rate_1_found = 0
    rate_5_found = 0

    for (rate, months, label), expected_str in EXPECTED_STRINGS.items():
        if expected_str in output:
            if rate == 1:
                rate_1_found += 1
            elif rate == 5:
                rate_5_found += 1

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


def _check_loan_terms(items: List[RubricItem], output: str):
    """Check (main_f): displays payment amounts for 3, 5, and 6 year loans."""
    item = get_item(items, "main_f")

    terms_found = {36: False, 60: False, 72: False}

    for (rate, months, label), expected_str in EXPECTED_STRINGS.items():
        if expected_str in output:
            terms_found[months] = True

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


def _check_formula_via_output(items: List[RubricItem], output: str):
    """
    Check (class_d_i): verify formula correctness by comparing output values.
    If all expected values appear in output, formula is correct.
    """
    item = get_item(items, "class_d_i")

    total_expected = len(EXPECTED_STRINGS)
    found = sum(1 for v in EXPECTED_STRINGS.values() if v in output)

    if found == total_expected:
        # All values match - formula is definitely correct
        item.deduction = 0
        item.passed = True
        item.notes = "Formula verified: all output values match expected"
    elif found > total_expected // 2:
        # Most values match - formula likely correct, minor rounding differences
        item.deduction = 0
        item.passed = True
        item.notes = f"Formula mostly correct: {found}/{total_expected} values match"
    elif found > 0:
        # Some match - partial credit
        item.deduction = 5
        item.passed = False
        item.notes = f"Formula partially correct: only {found}/{total_expected} values match"
    # If found == 0, keep whatever was set by the AST check
