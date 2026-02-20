"""PA3 Customer Loan Accounts rubric item definitions."""

from framework.rubric import RubricItem


def create_pa3_rubric() -> list:
    """Create the list of rubric items for PA3."""
    return [
        # --- Customer Class ---
        RubricItem(
            id="cust_props",
            category="Customer Class",
            description="Has properties: firstName, lastName, SSN, loanAccounts (ArrayList<LoanAccount>)",
            max_deduction=5
        ),
        RubricItem(
            id="cust_constructor",
            category="Customer Class",
            description="Has constructor with three parameters (firstName, lastName, SSN)",
            max_deduction=5
        ),
        RubricItem(
            id="cust_getter_firstname",
            category="Customer Class",
            description="Has getter for firstName",
            max_deduction=3
        ),
        RubricItem(
            id="cust_getter_lastname",
            category="Customer Class",
            description="Has getter for lastName",
            max_deduction=3
        ),
        RubricItem(
            id="cust_getter_ssn",
            category="Customer Class",
            description="Has getter for SSN",
            max_deduction=3
        ),
        RubricItem(
            id="cust_addloan",
            category="Customer Class",
            description="Has addLoanAccount(LoanAccount) method",
            max_deduction=10
        ),
        RubricItem(
            id="cust_printreport",
            category="Customer Class",
            description="Has printMonthlyReport() method that prints all loan info using toString()",
            max_deduction=15
        ),

        # --- Main Method ---
        RubricItem(
            id="main_code",
            category="Main Method",
            description="Uses the main method code as given in the assignment",
            max_deduction=10
        ),
        RubricItem(
            id="main_format",
            category="Main Method",
            description="Displays data with $ and % symbols as shown in output",
            max_deduction=5
        ),
        RubricItem(
            id="main_decimal",
            category="Main Method",
            description="Displays data with 2 decimal places for all dollar amounts",
            max_deduction=5
        ),
        RubricItem(
            id="main_numbers",
            category="Main Method",
            description="All numbers match expected output (-2 per incorrect value)",
            max_deduction=10
        ),
    ]
