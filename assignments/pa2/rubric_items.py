"""PA2 Loan Account Hierarchy rubric item definitions."""

from framework.rubric import RubricItem


def create_pa2_rubric() -> list:
    """Create the list of rubric items for PA2."""
    return [
        # --- LoanAccount Class ---
        RubricItem(
            id="la_props",
            category="LoanAccount Class",
            description="Has properties: principal, annualInterestRate, months",
            max_deduction=5
        ),
        RubricItem(
            id="la_constructor",
            category="LoanAccount Class",
            description="Has constructor with three parameters",
            max_deduction=5
        ),
        RubricItem(
            id="la_calculate",
            category="LoanAccount Class",
            description="Has calculateMonthlyPayment() with no parameters and correct formula",
            max_deduction=10
        ),
        RubricItem(
            id="la_getters",
            category="LoanAccount Class",
            description="Has getters for the three property variables",
            max_deduction=5
        ),
        RubricItem(
            id="la_tostring",
            category="LoanAccount Class",
            description="Has toString() displaying principal, annualInterestRate, and months",
            max_deduction=10
        ),

        # --- CarLoan Class ---
        RubricItem(
            id="cl_extends",
            category="CarLoan Class",
            description="CarLoan is a subclass of LoanAccount",
            max_deduction=5
        ),
        RubricItem(
            id="cl_props",
            category="CarLoan Class",
            description="Has vehicleVIN property",
            max_deduction=5
        ),
        RubricItem(
            id="cl_constructor",
            category="CarLoan Class",
            description="Has constructor with four parameters (3 LoanAccount + VIN)",
            max_deduction=5
        ),
        RubricItem(
            id="cl_tostring",
            category="CarLoan Class",
            description="Has toString() displaying VIN number",
            max_deduction=5
        ),

        # --- PrimaryMortgage Class ---
        RubricItem(
            id="pm_extends",
            category="PrimaryMortgage Class",
            description="PrimaryMortgage is a subclass of LoanAccount",
            max_deduction=5
        ),
        RubricItem(
            id="pm_props",
            category="PrimaryMortgage Class",
            description="Has PMIMonthlyAmount and Address properties",
            max_deduction=5
        ),
        RubricItem(
            id="pm_constructor",
            category="PrimaryMortgage Class",
            description="Has constructor with five parameters (3 LoanAccount + PMI + Address)",
            max_deduction=5
        ),
        RubricItem(
            id="pm_tostring",
            category="PrimaryMortgage Class",
            description="Has toString() displaying PMIMonthlyAmount and Address",
            max_deduction=10
        ),

        # --- UnsecuredLoan Class ---
        RubricItem(
            id="ul_extends",
            category="UnsecuredLoan Class",
            description="UnsecuredLoan is a subclass of LoanAccount",
            max_deduction=5
        ),
        RubricItem(
            id="ul_constructor",
            category="UnsecuredLoan Class",
            description="Has constructor with three parameters (LoanAccount params)",
            max_deduction=5
        ),
        RubricItem(
            id="ul_tostring",
            category="UnsecuredLoan Class",
            description="Has toString() displaying unsecured loan info",
            max_deduction=10
        ),

        # --- Address Class ---
        RubricItem(
            id="addr_props",
            category="Address Class",
            description="Has properties: street, city, state, zipcode",
            max_deduction=5
        ),
        RubricItem(
            id="addr_constructor",
            category="Address Class",
            description="Has constructor with four parameters",
            max_deduction=5
        ),
        RubricItem(
            id="addr_getters",
            category="Address Class",
            description="Has getters for each property",
            max_deduction=5
        ),
        RubricItem(
            id="addr_tostring",
            category="Address Class",
            description="Has toString() displaying address information",
            max_deduction=10
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
            description="Displays data with $ and % symbols and 2 decimal places",
            max_deduction=5
        ),
    ]
