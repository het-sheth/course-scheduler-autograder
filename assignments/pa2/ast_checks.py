"""PA2-specific AST/static analysis checks for the Loan Account Hierarchy."""

import re
from typing import List, Dict, Optional
from framework.rubric import RubricItem
from framework.java_ast_analyzer import JavaASTAnalyzer
from pathlib import Path

NUMERIC_TYPES = {'double', 'float', 'Double', 'Float'}
INT_TYPES = {'int', 'Integer', 'long', 'Long'}
STRING_TYPES = {'String', 'string'}


def get_item(items: List[RubricItem], item_id: str) -> RubricItem:
    for item in items:
        if item.id == item_id:
            return item
    raise ValueError(f"Rubric item '{item_id}' not found")


def _build_class_map(java_files: List[Path], all_sources: dict) -> Dict[str, JavaASTAnalyzer]:
    """Map lowercase class names to their analyzers."""
    class_map = {}
    for f in java_files:
        source = all_sources.get(f, f.read_text(errors='ignore'))
        analyzer = JavaASTAnalyzer(source)
        for name in analyzer.get_class_names():
            class_map[name.lower()] = analyzer
    return class_map


def _find_analyzer(class_map: dict, *names) -> Optional[JavaASTAnalyzer]:
    """Find analyzer for a class by trying multiple name variants."""
    for name in names:
        if name.lower() in class_map:
            return class_map[name.lower()]
    return None


def _find_base_loan_class(class_map: dict):
    """Find the base loan account class by name variants or by characteristic properties.
    Returns (lowercase_name, analyzer) or (None, None)."""
    # Try known name variants first
    for name in ('loanaccount', 'loanaccounthierarchy', 'loan', 'loanclass', 'baseloan'):
        if name in class_map:
            return name, class_map[name]

    # Fallback: find by characteristic properties (principal + rate + months)
    skip = {'address', 'carloan', 'primarymortgage', 'unsecuredloan',
            'main', 'test', 'customer'}
    for name, analyzer in class_map.items():
        if name in skip:
            continue
        fields = analyzer.get_fields()
        field_names = {f.name.lower() for f in fields}
        has_principal = any(n in field_names for n in ('principal', 'principle', 'loanamount'))
        has_rate = any(n in field_names for n in ('annualinterestrate', 'annualinterest', 'interestrate', 'rate'))
        has_months = any(n in field_names for n in ('months', 'numberofmonths', 'term', 'nummonths', 'loanterm'))
        if has_principal and has_rate and has_months:
            return name, analyzer

    return None, None


def check_class_structure(java_files: List[Path], all_sources: dict, items: List[RubricItem]):
    """Run all PA2 class structure checks."""
    class_map = _build_class_map(java_files, all_sources)

    base_name = _check_loan_account(class_map, items)
    _check_car_loan(class_map, items, base_name)
    _check_primary_mortgage(class_map, items, base_name)
    _check_unsecured_loan(class_map, items, base_name)
    _check_address(class_map, items)


# ---- LoanAccount Class ----

def _check_loan_account(class_map: dict, items: List[RubricItem]) -> str:
    """Check LoanAccount class structure. Returns the lowercase name of the found base class."""
    base_name, analyzer = _find_base_loan_class(class_map)
    if not analyzer:
        for item_id in ('la_props', 'la_constructor', 'la_calculate', 'la_getters', 'la_tostring'):
            item = get_item(items, item_id)
            item.deduction = item.max_deduction
            item.passed = False
            item.notes = "LoanAccount class not found"
        return 'loanaccount'

    _check_la_properties(analyzer, items)
    _check_la_constructor(analyzer, items)
    _check_la_calculate(analyzer, items)
    _check_la_getters(analyzer, items)
    _check_la_tostring(analyzer, items)
    return base_name


def _check_la_properties(analyzer: JavaASTAnalyzer, items: List[RubricItem]):
    item = get_item(items, "la_props")
    fields = analyzer.get_fields()
    field_names = {f.name.lower() for f in fields}

    missing = []
    if not any(n in field_names for n in ('principal', 'principle', 'loanamount')):
        missing.append("principal")
    if not any(n in field_names for n in ('annualinterestrate', 'annualinterest', 'interestrate', 'rate')):
        missing.append("annualInterestRate")
    if not any(n in field_names for n in ('months', 'numberofmonths', 'term', 'nummonths', 'loanterm')):
        missing.append("months")

    if missing:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = f"Missing properties: {', '.join(missing)}"


def _check_la_constructor(analyzer: JavaASTAnalyzer, items: List[RubricItem]):
    item = get_item(items, "la_constructor")
    constructors = analyzer.get_constructors()

    matching = [c for c in constructors if len(c.param_types) == 3]
    if not matching:
        if constructors:
            item.deduction = item.max_deduction
            item.passed = False
            item.notes = f"No 3-parameter constructor (found {[len(c.param_types) for c in constructors]} params)"
        else:
            item.deduction = item.max_deduction
            item.passed = False
            item.notes = "No constructor found"


def _check_la_calculate(analyzer: JavaASTAnalyzer, items: List[RubricItem]):
    item = get_item(items, "la_calculate")
    methods = analyzer.get_methods()

    matching = [m for m in methods if m.name.lower() == "calculatemonthlypayment"]
    if not matching:
        matching = [m for m in methods if "monthly" in m.name.lower() and "payment" in m.name.lower()]
    if not matching:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "Method calculateMonthlyPayment not found"
        return

    method = matching[0]
    issues = []
    if method.return_type not in NUMERIC_TYPES:
        issues.append(f"return type '{method.return_type}', expected double")
    if len(method.param_types) != 0:
        issues.append(f"should take no parameters, found {len(method.param_types)}")

    # Check for Math.pow in the formula
    if not analyzer.source_contains(r'Math\.pow', re.IGNORECASE):
        issues.append("formula may not use Math.pow()")

    if issues:
        item.deduction = 5 if len(issues) == 1 else item.max_deduction
        item.passed = False
        item.notes = "calculateMonthlyPayment: " + "; ".join(issues)


def _check_la_getters(analyzer: JavaASTAnalyzer, items: List[RubricItem]):
    item = get_item(items, "la_getters")
    methods = analyzer.get_methods()
    method_names = {m.name.lower() for m in methods}

    getters_found = 0
    for getter in ('getprincipal', 'getannualinterestrate', 'getmonths',
                    'getprincipal', 'getinterestrate', 'getrate',
                    'getnumberofmonths', 'getterm', 'getloanterm'):
        if getter in method_names:
            getters_found += 1

    # Need at least 3 getters (one per property)
    if getters_found < 3:
        # Try broader search: any method starting with "get" that returns something
        get_methods = [m for m in methods if m.name.lower().startswith('get')
                       and m.return_type != 'void' and len(m.param_types) == 0]
        getters_found = len(get_methods)

    if getters_found < 3:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = f"Only {getters_found} getter(s) found, expected 3"


def _check_la_tostring(analyzer: JavaASTAnalyzer, items: List[RubricItem]):
    item = get_item(items, "la_tostring")
    methods = analyzer.get_methods()

    has_tostring = any(m.name == "toString" or m.name == "tostring" for m in methods)
    if not has_tostring:
        has_tostring = analyzer.source_contains(r'toString\s*\(', re.IGNORECASE)

    if not has_tostring:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "toString() method not found"


# ---- CarLoan Class ----

def _check_car_loan(class_map: dict, items: List[RubricItem], base_class_name: str = 'loanaccount'):
    analyzer = _find_analyzer(class_map, 'CarLoan', 'Carloan', 'carloan')
    if not analyzer:
        for item_id in ('cl_extends', 'cl_props', 'cl_constructor', 'cl_tostring'):
            item = get_item(items, item_id)
            item.deduction = item.max_deduction
            item.passed = False
            item.notes = "CarLoan class not found"
        return

    # Check extends
    item = get_item(items, "cl_extends")
    parent = analyzer.get_parent_class()
    if not parent or parent.lower() != base_class_name:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = f"CarLoan does not extend LoanAccount (extends: {parent or 'nothing'})"

    # Check vehicleVIN property
    item = get_item(items, "cl_props")
    fields = analyzer.get_fields()
    has_vin = any(f.name.lower() in ('vehiclevin', 'vin', 'vehicle_vin', 'vinnumber')
                  for f in fields)
    if not has_vin:
        has_vin = analyzer.source_contains(r'(?:vehicleVIN|vin|VIN)\b', re.IGNORECASE)
    if not has_vin:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "vehicleVIN property not found"

    # Check constructor (4 params)
    item = get_item(items, "cl_constructor")
    constructors = analyzer.get_constructors()
    matching = [c for c in constructors if len(c.param_types) == 4]
    if not matching:
        item.deduction = item.max_deduction
        item.passed = False
        param_counts = [len(c.param_types) for c in constructors] if constructors else []
        item.notes = f"No 4-parameter constructor found ({param_counts or 'none'})"

    # Check toString
    item = get_item(items, "cl_tostring")
    methods = analyzer.get_methods()
    has_tostring = any(m.name.lower() == "tostring" for m in methods)
    if not has_tostring:
        has_tostring = analyzer.source_contains(r'toString\s*\(')
    if not has_tostring:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "toString() method not found"


# ---- PrimaryMortgage Class ----

def _check_primary_mortgage(class_map: dict, items: List[RubricItem], base_class_name: str = 'loanaccount'):
    analyzer = _find_analyzer(class_map, 'PrimaryMortgage', 'Primarymortgage',
                              'primarymortgage', 'Mortgage', 'MortgageLoan')
    if not analyzer:
        for item_id in ('pm_extends', 'pm_props', 'pm_constructor', 'pm_tostring'):
            item = get_item(items, item_id)
            item.deduction = item.max_deduction
            item.passed = False
            item.notes = "PrimaryMortgage class not found"
        return

    # Check extends
    item = get_item(items, "pm_extends")
    parent = analyzer.get_parent_class()
    if not parent or parent.lower() != base_class_name:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = f"PrimaryMortgage does not extend LoanAccount (extends: {parent or 'nothing'})"

    # Check properties (PMIMonthlyAmount and Address)
    item = get_item(items, "pm_props")
    fields = analyzer.get_fields()
    field_names = {f.name.lower() for f in fields}
    field_types = {f.type_name.lower() for f in fields}

    has_pmi = any(n in field_names for n in ('pmimonthlyamount', 'pmi', 'pmimonthlypayment',
                                              'pmiamount', 'monthlyamount', 'pmimonthly'))
    has_address = any(n in field_names for n in ('address', 'propertyaddress', 'addr')) or \
                  'address' in field_types

    missing = []
    if not has_pmi:
        missing.append("PMIMonthlyAmount")
    if not has_address:
        missing.append("Address")
    if missing:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = f"Missing properties: {', '.join(missing)}"

    # Check constructor (5 params)
    item = get_item(items, "pm_constructor")
    constructors = analyzer.get_constructors()
    matching = [c for c in constructors if len(c.param_types) == 5]
    if not matching:
        # Also accept 4 params if address is composed differently
        matching = [c for c in constructors if len(c.param_types) >= 4]
    if not matching:
        item.deduction = item.max_deduction
        item.passed = False
        param_counts = [len(c.param_types) for c in constructors] if constructors else []
        item.notes = f"No 5-parameter constructor found ({param_counts or 'none'})"

    # Check toString
    item = get_item(items, "pm_tostring")
    methods = analyzer.get_methods()
    has_tostring = any(m.name.lower() == "tostring" for m in methods)
    if not has_tostring:
        has_tostring = analyzer.source_contains(r'toString\s*\(')
    if not has_tostring:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "toString() method not found"


# ---- UnsecuredLoan Class ----

def _check_unsecured_loan(class_map: dict, items: List[RubricItem], base_class_name: str = 'loanaccount'):
    analyzer = _find_analyzer(class_map, 'UnsecuredLoan', 'Unsecuredloan',
                              'unsecuredloan', 'PersonalLoan')
    if not analyzer:
        for item_id in ('ul_extends', 'ul_constructor', 'ul_tostring'):
            item = get_item(items, item_id)
            item.deduction = item.max_deduction
            item.passed = False
            item.notes = "UnsecuredLoan class not found"
        return

    # Check extends
    item = get_item(items, "ul_extends")
    parent = analyzer.get_parent_class()
    if not parent or parent.lower() != base_class_name:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = f"UnsecuredLoan does not extend LoanAccount (extends: {parent or 'nothing'})"

    # Check constructor (3 params)
    item = get_item(items, "ul_constructor")
    constructors = analyzer.get_constructors()
    matching = [c for c in constructors if len(c.param_types) == 3]
    if not matching:
        item.deduction = item.max_deduction
        item.passed = False
        param_counts = [len(c.param_types) for c in constructors] if constructors else []
        item.notes = f"No 3-parameter constructor found ({param_counts or 'none'})"

    # Check toString
    item = get_item(items, "ul_tostring")
    methods = analyzer.get_methods()
    has_tostring = any(m.name.lower() == "tostring" for m in methods)
    if not has_tostring:
        has_tostring = analyzer.source_contains(r'toString\s*\(')
    if not has_tostring:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "toString() method not found"


# ---- Address Class ----

def _check_address(class_map: dict, items: List[RubricItem]):
    analyzer = _find_analyzer(class_map, 'Address', 'address')
    if not analyzer:
        for item_id in ('addr_props', 'addr_constructor', 'addr_getters', 'addr_tostring'):
            item = get_item(items, item_id)
            item.deduction = item.max_deduction
            item.passed = False
            item.notes = "Address class not found"
        return

    # Check properties
    item = get_item(items, "addr_props")
    fields = analyzer.get_fields()
    field_names = {f.name.lower() for f in fields}

    missing = []
    if not any(n in field_names for n in ('street', 'streetaddress', 'address', 'housenumber')):
        missing.append("street")
    if not any(n in field_names for n in ('city', 'cityname')):
        missing.append("city")
    if not any(n in field_names for n in ('state', 'statename', 'st')):
        missing.append("state")
    if not any(n in field_names for n in ('zipcode', 'zip', 'postalcode', 'zipcode')):
        missing.append("zipcode")

    if missing:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = f"Missing properties: {', '.join(missing)}"

    # Check constructor (4 params)
    item = get_item(items, "addr_constructor")
    constructors = analyzer.get_constructors()
    matching = [c for c in constructors if len(c.param_types) == 4]
    if not matching:
        item.deduction = item.max_deduction
        item.passed = False
        param_counts = [len(c.param_types) for c in constructors] if constructors else []
        item.notes = f"No 4-parameter constructor found ({param_counts or 'none'})"

    # Check getters (4 getters)
    item = get_item(items, "addr_getters")
    methods = analyzer.get_methods()
    method_names = {m.name.lower() for m in methods}

    getters_found = 0
    for getter in ('getstreet', 'getcity', 'getstate', 'getzipcode',
                    'getzip', 'getpostalcode', 'getaddress'):
        if getter in method_names:
            getters_found += 1

    if getters_found < 4:
        get_methods = [m for m in methods if m.name.lower().startswith('get')
                       and m.return_type != 'void' and len(m.param_types) == 0]
        getters_found = len(get_methods)

    if getters_found < 4:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = f"Only {getters_found} getter(s) found, expected 4"

    # Check toString
    item = get_item(items, "addr_tostring")
    methods = analyzer.get_methods()
    has_tostring = any(m.name.lower() == "tostring" for m in methods)
    if not has_tostring:
        has_tostring = analyzer.source_contains(r'toString\s*\(')
    if not has_tostring:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "toString() method not found"
