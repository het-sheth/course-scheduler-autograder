"""PA3-specific AST/static analysis checks for the Customer Loan Accounts."""

import re
from typing import List, Dict, Optional
from framework.rubric import RubricItem
from framework.java_ast_analyzer import JavaASTAnalyzer
from pathlib import Path


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
    """Find analyzer for a class by trying exact names, then substring match."""
    # Exact match first
    for name in names:
        if name.lower() in class_map:
            return class_map[name.lower()]
    # Substring match: find any class whose name contains one of the search terms
    for name in names:
        key = name.lower()
        for class_name, analyzer in class_map.items():
            if key in class_name:
                return analyzer
    return None


def _find_customer_class(class_map: dict) -> Optional[JavaASTAnalyzer]:
    """Find the Customer class by name variants or characteristic properties."""
    # Try exact/substring name match
    result = _find_analyzer(class_map, 'Customer')
    if result:
        return result

    # Fallback: find by characteristic properties (firstName + lastName + SSN + ArrayList)
    skip = {'address', 'carloan', 'primarymortgage', 'unsecuredloan',
            'loanaccount', 'loanaccounthierarchy', 'main', 'test'}
    for name, analyzer in class_map.items():
        if name in skip:
            continue
        fields = analyzer.get_fields()
        field_names = {f.name.lower() for f in fields}
        field_types = {f.type_name.lower() for f in fields}
        has_first = any(n in field_names for n in ('firstname', 'first_name', 'fname', 'first'))
        has_last = any(n in field_names for n in ('lastname', 'last_name', 'lname', 'last'))
        has_ssn = any(n in field_names for n in ('ssn', 'socialsecuritynumber', 'social'))
        has_list = any('arraylist' in t or 'list' in t for t in field_types)
        if has_first and has_last and has_ssn and has_list:
            return analyzer

    return None


def check_class_structure(java_files: List[Path], all_sources: dict, items: List[RubricItem]):
    """Run all PA3 class structure checks."""
    class_map = _build_class_map(java_files, all_sources)
    _check_customer(class_map, all_sources, items)


# ---- Customer Class ----

def _check_customer(class_map: dict, all_sources: dict, items: List[RubricItem]):
    analyzer = _find_customer_class(class_map)
    if not analyzer:
        for item_id in ('cust_props', 'cust_constructor', 'cust_getter_firstname',
                        'cust_getter_lastname', 'cust_getter_ssn',
                        'cust_addloan', 'cust_printreport'):
            item = get_item(items, item_id)
            item.deduction = item.max_deduction
            item.passed = False
            item.notes = "Customer class not found"
        return

    _check_customer_properties(analyzer, all_sources, items)
    _check_customer_constructor(analyzer, items)
    _check_customer_getters(analyzer, items)
    _check_customer_addloan(analyzer, all_sources, items)
    _check_customer_printreport(analyzer, all_sources, items)


def _check_customer_properties(analyzer: JavaASTAnalyzer, all_sources: dict, items: List[RubricItem]):
    item = get_item(items, "cust_props")
    fields = analyzer.get_fields()
    field_names = {f.name.lower() for f in fields}
    field_types = {f.type_name.lower() for f in fields}

    # Also search all source for the Customer class content via regex
    combined = "\n".join(all_sources.values())

    missing = []
    if not any(n in field_names for n in ('firstname', 'first_name', 'fname', 'first')):
        # Regex fallback
        if not re.search(r'(?:String|string)\s+(?:firstName|first_name|fname)', combined):
            missing.append("firstName")
    if not any(n in field_names for n in ('lastname', 'last_name', 'lname', 'last')):
        if not re.search(r'(?:String|string)\s+(?:lastName|last_name|lname)', combined):
            missing.append("lastName")
    if not any(n in field_names for n in ('ssn', 'socialsecuritynumber', 'social', 'socialsecurity')):
        if not re.search(r'(?:String|string)\s+(?:SSN|ssn|socialSecurityNumber)', combined):
            missing.append("SSN")
    if not any(n in field_names for n in ('loanaccounts', 'loans', 'loanlist', 'accounts',
                                           'loan_accounts', 'loanaccount')):
        # Check for ArrayList field type
        has_arraylist = any('arraylist' in t or 'list' in t for t in field_types)
        if not has_arraylist:
            if not re.search(r'ArrayList\s*<\s*LoanAccount\s*>', combined):
                missing.append("loanAccounts (ArrayList<LoanAccount>)")

    if missing:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = f"Missing properties: {', '.join(missing)}"


def _check_customer_constructor(analyzer: JavaASTAnalyzer, items: List[RubricItem]):
    item = get_item(items, "cust_constructor")
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


def _check_customer_getters(analyzer: JavaASTAnalyzer, items: List[RubricItem]):
    methods = analyzer.get_methods()
    method_names = {m.name.lower() for m in methods}

    # Check getter for firstName
    item = get_item(items, "cust_getter_firstname")
    has_getter = any(n in method_names for n in ('getfirstname', 'getfname', 'getfirst'))
    if not has_getter:
        # Broader: any getter that returns String and has 'first' or 'name' in it
        has_getter = any(m.name.lower().startswith('get') and 'first' in m.name.lower()
                        for m in methods)
    if not has_getter:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "getFirstName() not found"

    # Check getter for lastName
    item = get_item(items, "cust_getter_lastname")
    has_getter = any(n in method_names for n in ('getlastname', 'getlname', 'getlast'))
    if not has_getter:
        has_getter = any(m.name.lower().startswith('get') and 'last' in m.name.lower()
                        for m in methods)
    if not has_getter:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "getLastName() not found"

    # Check getter for SSN
    item = get_item(items, "cust_getter_ssn")
    has_getter = any(n in method_names for n in ('getssn', 'getsocialsecuritynumber', 'getsocial'))
    if not has_getter:
        has_getter = any(m.name.lower().startswith('get') and 'ss' in m.name.lower()
                        for m in methods)
    if not has_getter:
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "getSSN() not found"


def _check_customer_addloan(analyzer: JavaASTAnalyzer, all_sources: dict, items: List[RubricItem]):
    item = get_item(items, "cust_addloan")
    methods = analyzer.get_methods()

    # Look for addLoanAccount or similar method
    matching = [m for m in methods if m.name.lower() in ('addloanaccount', 'addloan', 'addaccount')]
    if not matching:
        # Broader search: method with 'add' and 'loan' or 'account'
        matching = [m for m in methods
                    if 'add' in m.name.lower() and
                    ('loan' in m.name.lower() or 'account' in m.name.lower())]
    if not matching:
        # Regex fallback in source
        combined = "\n".join(all_sources.values())
        if re.search(r'void\s+add\w*(?:Loan|Account)\s*\(', combined, re.IGNORECASE):
            return  # Found via regex, pass
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "addLoanAccount() method not found"
        return

    method = matching[0]
    if len(method.param_types) != 1:
        item.deduction = 5
        item.passed = False
        item.notes = f"addLoanAccount should take 1 parameter, found {len(method.param_types)}"


def _check_customer_printreport(analyzer: JavaASTAnalyzer, all_sources: dict, items: List[RubricItem]):
    item = get_item(items, "cust_printreport")
    methods = analyzer.get_methods()

    # Look for printMonthlyReport or similar
    matching = [m for m in methods if m.name.lower() in ('printmonthlyreport', 'printreport',
                                                          'monthlyreport', 'printloanreport')]
    if not matching:
        matching = [m for m in methods
                    if 'print' in m.name.lower() and 'report' in m.name.lower()]
    if not matching:
        matching = [m for m in methods
                    if 'print' in m.name.lower() and 'monthly' in m.name.lower()]
    if not matching:
        # Regex fallback
        combined = "\n".join(all_sources.values())
        if re.search(r'void\s+print\w*(?:Monthly|Report)\s*\(', combined, re.IGNORECASE):
            return  # Found via regex, pass
        item.deduction = item.max_deduction
        item.passed = False
        item.notes = "printMonthlyReport() method not found"
        return

    method = matching[0]
    if method.return_type and method.return_type != 'void':
        item.deduction = 5
        item.passed = False
        item.notes = f"printMonthlyReport should return void, found {method.return_type}"
