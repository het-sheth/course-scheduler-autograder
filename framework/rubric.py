"""Data classes for rubric items and grading results."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class RubricItem:
    id: str
    category: str
    description: str
    max_deduction: int
    deduction: int = 0
    passed: bool = True
    notes: str = ""

    @property
    def earned(self) -> bool:
        return self.deduction == 0


@dataclass
class GradingResult:
    student_name: str
    student_id: str
    rubric_items: List[RubricItem] = field(default_factory=list)
    total_score: int = 100
    max_score: int = 100
    compilation_success: bool = False
    execution_success: bool = False
    actual_output: str = ""
    source_code: str = ""
    compiler_errors: str = ""
    oop_notes: List[str] = field(default_factory=list)
    error_message: str = ""

    def calculate_score(self):
        total_deductions = sum(item.deduction for item in self.rubric_items)
        oop_deduction = min(len(self.oop_notes) * 2, 15)
        self.total_score = max(0, self.max_score - total_deductions - oop_deduction)

    @property
    def letter_grade(self) -> str:
        s = self.total_score
        if s >= 93: return "A"
        if s >= 90: return "A-"
        if s >= 87: return "B+"
        if s >= 83: return "B"
        if s >= 80: return "B-"
        if s >= 77: return "C+"
        if s >= 70: return "C"
        if s >= 60: return "D"
        return "F"

    @property
    def class_deductions(self) -> int:
        return sum(i.deduction for i in self.rubric_items if i.category == "LoanAccount Class")

    @property
    def main_deductions(self) -> int:
        return sum(i.deduction for i in self.rubric_items if i.category == "Main Method")
