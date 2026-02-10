"""PA1-specific AST/static analysis checks."""

import re
from typing import List
from framework.rubric import RubricItem
from framework.java_ast_analyzer import JavaASTAnalyzer

# Types that are acceptable as numeric types for this assignment
NUMERIC_TYPES = {'double', 'float', 'Double', 'Float'}
INT_TYPES = {'int', 'Integer', 'long', 'Long'}


def get_item(items: List[RubricItem], item_id: str) -> RubricItem:
    for item in items:
        if item.id == item_id:
            return item
    raise ValueError(f"Rubric item '{item_id}' not found")


def check_class_structure(analyzer: JavaASTAnalyzer, items: List[RubricItem]):
    """Run all PA1 class structure checks against the AST."""

    fields = analyzer.get_fields()
    methods = analyzer.get_methods()
    constructors = analyzer.get_constructors()

    _check_annual_interest_rate(fields, items)
    _check_principal(fields, items)
    _check_constructor(constructors, items)
    _check_calculate_monthly_payment(methods, analyzer, items)
    _check_set_annual_interest_rate(methods, items)
    _check_loan_objects(analyzer, items)


def _check_annual_interest_rate(fields, items: List[RubricItem]):
    """Check (a): private static annualInterestRate."""
    item = get_item(items, "class_a")

    # Case-insensitive match, also match common variants
    matching = [f for f in fields if f.name.lower() in
                ("annualinterestrate", "annualinterest", "annual_interest_rate")]
    if not matching:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "Field 'annualInterestRate' not found"
        return

    field = matching[0]
    issues = []

    if 'private' not in field.modifiers:
        issues.append("not declared as private")
    if 'static' not in field.modifiers:
        issues.append("not declared as static")
    if field.type_name not in NUMERIC_TYPES:
        issues.append(f"type is '{field.type_name}', expected 'double'")

    if issues:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "annualInterestRate: " + "; ".join(issues)


def _check_principal(fields, items: List[RubricItem]):
    """Check (b): private instance variable principal."""
    item = get_item(items, "class_b")

    matching = [f for f in fields if f.name.lower() in ("principal", "loanamount", "loan_amount")]
    if not matching:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "Field 'principal' not found"
        return

    field = matching[0]
    issues = []

    if 'private' not in field.modifiers:
        issues.append("not declared as private")
    if field.type_name not in NUMERIC_TYPES:
        issues.append(f"type is '{field.type_name}', expected 'double'")

    if issues:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "principal: " + "; ".join(issues)


def _check_constructor(constructors, items: List[RubricItem]):
    """Check (c): constructor with one parameter, principal."""
    item = get_item(items, "class_c")

    if not constructors:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "No constructor found"
        return

    # Look for a single-parameter constructor
    single_param = [c for c in constructors if len(c.param_types) == 1]
    if not single_param:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = (f"No single-parameter constructor found "
                      f"(found constructors with {[len(c.param_types) for c in constructors]} params)")
        return

    c = single_param[0]
    if c.param_types[0] not in NUMERIC_TYPES:
        item.deduction = 3
        item.passed = False
        item.notes = f"Constructor parameter type is '{c.param_types[0]}', expected 'double'"


def _check_calculate_monthly_payment(methods, analyzer: JavaASTAnalyzer, items: List[RubricItem]):
    """Check (d): calculateMonthlyPayment method exists with correct signature."""
    item = get_item(items, "class_d")

    # Case-insensitive match on method name
    matching = [m for m in methods if m.name.lower() == "calculatemonthlypayment"]
    if not matching:
        # Also try partial match - method name contains "monthly" and "payment"
        matching = [m for m in methods if "monthly" in m.name.lower() and "payment" in m.name.lower()]
    if not matching:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "Method 'calculateMonthlyPayment' not found"
        return

    method = matching[0]
    issues = []

    if method.return_type not in NUMERIC_TYPES:
        issues.append(f"return type is '{method.return_type}', expected 'double'")
    if len(method.param_types) != 1:
        issues.append(f"expected 1 parameter, found {len(method.param_types)}")
    elif method.param_types[0] not in INT_TYPES:
        issues.append(f"parameter type is '{method.param_types[0]}', expected 'int'")

    if issues:
        item.deduction = 5
        item.passed = False
        item.notes = "calculateMonthlyPayment: " + "; ".join(issues)

    # Check (d.i): formula check via AST - look for Math.pow usage
    formula_item = get_item(items, "class_d_i")
    has_math_pow = analyzer.source_contains(r'Math\.pow', re.IGNORECASE)

    if not has_math_pow:
        formula_item.deduction = formula_item.max_deduction
        formula_item.passed = False
        formula_item.notes = "Formula does not use Math.pow() - may be incorrect"
    # Final formula verification done via output check in output_checks.py


def _check_set_annual_interest_rate(methods, items: List[RubricItem]):
    """Check (e): static method setAnnualInterestRate."""
    item = get_item(items, "class_e")

    # Case-insensitive, also accept variants
    matching = [m for m in methods if m.name.lower() in
                ("setannualinterestrate", "setinterestrate", "setannualrate", "set_annual_interest_rate")]
    if not matching:
        # Broader: any static setter-like method with "rate" in name
        matching = [m for m in methods if m.name.lower().startswith("set")
                    and "rate" in m.name.lower() and 'static' in m.modifiers]
    if not matching:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "Method 'setAnnualInterestRate' not found"
        return

    method = matching[0]
    issues = []

    if 'static' not in method.modifiers:
        issues.append("not declared as static")
    if len(method.param_types) != 1:
        issues.append(f"expected 1 parameter, found {len(method.param_types)}")

    if issues:
        item.deduction = 5
        item.passed = False
        item.notes = "setAnnualInterestRate: " + "; ".join(issues)


def _check_loan_objects(analyzer: JavaASTAnalyzer, items: List[RubricItem]):
    """
    Check (main_a): creates loan1($5000) and loan2($31000).
    Uses regex on source. Accepts various number formats:
    5000, 5000.0, 5000.00, 5_000, 5000d, 5000f, etc.
    This is a soft check - output_checks will override if output proves
    the objects were created correctly.
    """
    item = get_item(items, "main_a")

    # Match new <Class>(<5000 variant>) - handles underscores, suffixes, decimals
    loan1_pattern = r'new\s+\w+\s*\(\s*5[_,]?000(?:\.\d*)?\s*[dfDF]?\s*\)'
    loan2_pattern = r'new\s+\w+\s*\(\s*31[_,]?000(?:\.\d*)?\s*[dfDF]?\s*\)'

    has_loan1 = analyzer.source_contains(loan1_pattern)
    has_loan2 = analyzer.source_contains(loan2_pattern)

    # Also check for variable-based construction (e.g., double amt = 5000; new Loan(amt))
    if not has_loan1:
        has_loan1 = analyzer.source_contains(r'5[_,]?000(?:\.\d*)?') and analyzer.source_contains(r'new\s+\w+\s*\(')
    if not has_loan2:
        has_loan2 = analyzer.source_contains(r'31[_,]?000(?:\.\d*)?') and analyzer.source_contains(r'new\s+\w+\s*\(')

    if not has_loan1 and not has_loan2:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "Neither loan1($5000) nor loan2($31000) found in source"
    elif not has_loan1:
        item.deduction = 5
        item.passed = False
        item.notes = "loan1 with $5000 principal not found"
    elif not has_loan2:
        item.deduction = 5
        item.passed = False
        item.notes = "loan2 with $31000 principal not found"
