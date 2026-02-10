"""PA2 Loan Account Hierarchy Grader."""

from typing import List

from framework.base_grader import BaseGrader
from framework.rubric import RubricItem
from assignments.pa2.rubric_items import create_pa2_rubric
from assignments.pa2.ast_checks import check_class_structure as pa2_ast_checks
from assignments.pa2.output_checks import check_output as pa2_output_checks
from assignments.pa2.expected_values import get_expected_output_text

# Fields already covered by PA2 rubric items - skip in OOP checks
PA2_RUBRIC_FIELDS = {'principal', 'annualinterestrate', 'months', 'vehiclevin',
                     'pmimonthlyamount', 'address', 'street', 'city', 'state', 'zipcode'}


class PA2Grader(BaseGrader):
    """Grader for Programming Assignment 2: Loan Account Hierarchy."""

    def define_rubric(self) -> List[RubricItem]:
        return create_pa2_rubric()

    def check_class_structure(self, items: List[RubricItem]):
        pa2_ast_checks(self.java_files, self.all_sources, items)

    def check_output(self, items: List[RubricItem], output: str):
        pa2_output_checks(items, output)

    def get_expected_output(self) -> str:
        return get_expected_output_text()

    def check_oop_practices(self) -> List[str]:
        notes = []
        if not self.analyzer:
            return notes
        for f in self.analyzer.get_fields():
            if f.name.lower() in PA2_RUBRIC_FIELDS:
                continue
            if 'private' not in f.modifiers and f.name not in ('args',):
                if 'public' in f.modifiers or not f.modifiers:
                    notes.append(f"Field '{f.name}' should be private")
        return notes
