"""PA1 Loan Account rubric item definitions."""

from framework.rubric import RubricItem


def create_pa1_rubric() -> list:
    """Create the list of rubric items for PA1."""
    return [
        # LoanAccount Class checks
        RubricItem(
            id="class_a",
            category="LoanAccount Class",
            description="Has private static instance variable annualInterestRate",
            max_deduction=5
        ),
        RubricItem(
            id="class_b",
            category="LoanAccount Class",
            description="Has private instance variable principal",
            max_deduction=5
        ),
        RubricItem(
            id="class_c",
            category="LoanAccount Class",
            description="Has constructor with one parameter, principal",
            max_deduction=5
        ),
        RubricItem(
            id="class_d",
            category="LoanAccount Class",
            description="Has calculateMonthlyPayment method with parameter numberOfPayments",
            max_deduction=10
        ),
        RubricItem(
            id="class_d_i",
            category="LoanAccount Class",
            description="Has proper formula to calculate payment and return it",
            max_deduction=10
        ),
        RubricItem(
            id="class_e",
            category="LoanAccount Class",
            description="Has a static method setAnnualInterestRate to set the annual interest rate",
            max_deduction=10
        ),

        # Main Method checks
        RubricItem(
            id="main_a",
            category="Main Method",
            description="Creates two LoanAccount objects, loan1 and loan2 with proper initial principal amounts",
            max_deduction=10
        ),
        RubricItem(
            id="main_b",
            category="Main Method",
            description="Displays the heading lines for each interest rate properly",
            max_deduction=5
        ),
        RubricItem(
            id="main_c",
            category="Main Method",
            description="Displays the loan data as columnar output",
            max_deduction=10
        ),
        RubricItem(
            id="main_d",
            category="Main Method",
            description="Displays the data with 2 decimal places for all dollar amounts",
            max_deduction=5
        ),
        RubricItem(
            id="main_e",
            category="Main Method",
            description="Displays the information at 1% and 5% interest rates",
            max_deduction=10
        ),
        RubricItem(
            id="main_f",
            category="Main Method",
            description="Displays the payment amounts for 3, 5, and 6 year loans",
            max_deduction=10
        ),
    ]
