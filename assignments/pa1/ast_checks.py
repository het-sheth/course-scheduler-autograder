"""PA1-specific AST/static analysis checks."""

import re
from typing import List
from framework.rubric import RubricItem
from framework.java_ast_analyzer import JavaASTAnalyzer


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

    matching = [f for f in fields if f.name.lower() == "annualinterestrate"]
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
    if field.type_name != 'double':
        issues.append(f"type is '{field.type_name}', expected 'double'")

    if issues:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "annualInterestRate: " + "; ".join(issues)


def _check_principal(fields, items: List[RubricItem]):
    """Check (b): private instance variable principal."""
    item = get_item(items, "class_b")

    matching = [f for f in fields if f.name.lower() == "principal"]
    if not matching:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "Field 'principal' not found"
        return

    field = matching[0]
    issues = []

    if 'private' not in field.modifiers:
        issues.append("not declared as private")
    if field.type_name != 'double':
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
        item.notes = f"No single-parameter constructor found (found constructors with {[len(c.param_types) for c in constructors]} params)"
        return

    c = single_param[0]
    if c.param_types[0] != 'double':
        item.deduction = 3
        item.passed = False
        item.notes = f"Constructor parameter type is '{c.param_types[0]}', expected 'double'"


def _check_calculate_monthly_payment(methods, analyzer: JavaASTAnalyzer, items: List[RubricItem]):
    """Check (d): calculateMonthlyPayment method exists with correct signature."""
    item = get_item(items, "class_d")

    # Case-insensitive match on method name
    matching = [m for m in methods if m.name.lower() == "calculatemonthlypayment"]
    if not matching:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "Method 'calculateMonthlyPayment' not found"
        return

    method = matching[0]
    issues = []

    if method.return_type != 'double':
        issues.append(f"return type is '{method.return_type}', expected 'double'")
    if len(method.param_types) != 1:
        issues.append(f"expected 1 parameter, found {len(method.param_types)}")
    elif method.param_types[0] != 'int':
        issues.append(f"parameter type is '{method.param_types[0]}', expected 'int'")

    if issues:
        item.deduction = 5
        item.passed = False
        item.notes = "calculateMonthlyPayment: " + "; ".join(issues)

    # Check (d.i): formula check via AST - look for Math.pow usage
    formula_item = get_item(items, "class_d_i")
    has_math_pow = analyzer.source_contains(r'Math\.pow')
    has_division = analyzer.source_contains(r'monthlyInterest\s*/\s*\(|monthlyRate\s*/\s*\(|monthly\w*\s*/\s*\(')

    if not has_math_pow:
        formula_item.deduction = formula_item.max_deduction
        formula_item.passed = False
        formula_item.notes = "Formula does not use Math.pow() - may be incorrect"
    # Final formula verification done via output check in output_checks.py


def _check_set_annual_interest_rate(methods, items: List[RubricItem]):
    """Check (e): static method setAnnualInterestRate."""
    item = get_item(items, "class_e")

    matching = [m for m in methods if m.name.lower() == "setannualinterestrate"]
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
    """Check (main_a): creates loan1($5000) and loan2($31000) via AST/regex."""
    item = get_item(items, "main_a")

    has_loan1 = analyzer.source_contains(r'new\s+\w+\s*\(\s*5000(?:\.0*)?\s*\)')
    has_loan2 = analyzer.source_contains(r'new\s+\w+\s*\(\s*31000(?:\.0*)?\s*\)')

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
