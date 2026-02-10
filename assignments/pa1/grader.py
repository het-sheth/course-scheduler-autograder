"""PA1 Loan Account Grader."""

from typing import List
from pathlib import Path

from framework.base_grader import BaseGrader
from framework.rubric import RubricItem
from assignments.pa1.rubric_items import create_pa1_rubric
from assignments.pa1.ast_checks import check_class_structure as pa1_ast_checks
from assignments.pa1.output_checks import check_output as pa1_output_checks
from assignments.pa1.expected_values import get_expected_output_text

# Fields already covered by PA1 rubric items - skip in OOP checks to avoid double-counting
PA1_RUBRIC_FIELDS = {'annualInterestRate', 'principal'}


class PA1Grader(BaseGrader):
    """Grader for Programming Assignment 1: Loan Account."""

    def define_rubric(self) -> List[RubricItem]:
        return create_pa1_rubric()

    def check_class_structure(self, items: List[RubricItem]):
        pa1_ast_checks(self.analyzer, items)

    def check_output(self, items: List[RubricItem], output: str):
        pa1_output_checks(items, output)

    def get_expected_output(self) -> str:
        return get_expected_output_text()

    def check_oop_practices(self) -> List[str]:
        notes = []
        if not self.analyzer:
            return notes
        for f in self.analyzer.get_fields():
            if f.name in PA1_RUBRIC_FIELDS:
                continue  # Already penalized by rubric items
            if 'private' not in f.modifiers and f.name not in ('args',):
                if 'public' in f.modifiers or not f.modifiers:
                    notes.append(f"Field '{f.name}' should be private")
        return notes
