"""PA1 Loan Account Grader."""

from typing import List
from pathlib import Path

from framework.base_grader import BaseGrader
from framework.rubric import RubricItem
from assignments.pa1.rubric_items import create_pa1_rubric
from assignments.pa1.ast_checks import check_class_structure as pa1_ast_checks
from assignments.pa1.output_checks import check_output as pa1_output_checks


class PA1Grader(BaseGrader):
    """Grader for Programming Assignment 1: Loan Account."""

    def define_rubric(self) -> List[RubricItem]:
        return create_pa1_rubric()

    def check_class_structure(self, items: List[RubricItem]):
        pa1_ast_checks(self.analyzer, items)

    def check_output(self, items: List[RubricItem], output: str):
        pa1_output_checks(items, output)
