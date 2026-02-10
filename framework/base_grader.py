"""Abstract base class for assignment graders."""

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Union

from framework.rubric import RubricItem, GradingResult
from framework.java_ast_analyzer import JavaASTAnalyzer
from framework.java_compiler import JavaCompiler
from framework.utils import create_temp_dir, cleanup_temp_dir


class BaseGrader(ABC):
    """
    Base class all assignment graders inherit from.
    Implements the grading pipeline: AST analysis -> compile -> run -> output check.
    """

    def __init__(self, java_files: Union[Path, List[Path]], student_name: str, student_id: str):
        if isinstance(java_files, Path):
            java_files = [java_files]
        self.java_files = java_files
        self.student_name = student_name
        self.student_id = student_id
        self.source_code = ""
        self.analyzer = None
        self.work_dir = create_temp_dir(f"grade_{student_name}_")

    def _find_class_file(self) -> Path:
        """
        Find the primary class file for AST analysis (not the test/main file).
        Heuristic: prefer files WITHOUT main(), then prefer files without 'test'/'main' in name.
        """
        if len(self.java_files) == 1:
            return self.java_files[0]

        # Separate files by whether they have main()
        main_pattern = re.compile(r'public\s+static\s+void\s+main')
        non_main = []
        with_main = []
        for f in self.java_files:
            source = f.read_text(errors='ignore')
            if main_pattern.search(source):
                with_main.append(f)
            else:
                non_main.append(f)

        # Prefer non-main files (the class definition)
        if non_main:
            # Among non-main files, avoid ones named 'test' or 'main'
            for f in non_main:
                if 'test' not in f.stem.lower() and 'main' not in f.stem.lower():
                    return f
            return non_main[0]

        # All files have main - pick the one without 'test'/'main' in name
        for f in with_main:
            if 'test' not in f.stem.lower() and 'main' not in f.stem.lower():
                return f
        return with_main[0]

    def grade(self) -> GradingResult:
        """Template method: run the full grading pipeline."""
        # Read all source files (stored on self for subclass access)
        self.all_sources = {}
        for f in self.java_files:
            self.all_sources[f] = f.read_text(errors='ignore')

        combined_source = "\n".join(self.all_sources.values())

        # Build display source with file headers
        if len(self.java_files) > 1:
            parts = []
            for f in self.java_files:
                parts.append(f"// === {f.name} ===\n{self.all_sources[f]}")
            self.source_code = "\n\n".join(parts)
        else:
            self.source_code = self.all_sources[self.java_files[0]]

        # Create AST analyzer from the class file
        class_file = self._find_class_file()
        self.analyzer = JavaASTAnalyzer(self.all_sources[class_file])
        # Allow source_contains to search ALL files
        self.analyzer.all_source = combined_source

        # Define rubric items
        rubric_items = self.define_rubric()

        # Phase 1: Static analysis
        self.check_class_structure(rubric_items)

        # Phase 2: Compile (all files)
        compiler = JavaCompiler(self.java_files, self.work_dir)
        compile_ok, compile_errors = compiler.compile()

        # Phase 3: Run
        run_ok = False
        output = ""
        if compile_ok:
            run_ok, output = compiler.run()

        # Phase 4: Output verification
        if run_ok:
            self.check_output(rubric_items, output)
        else:
            # If we can't run, apply deductions for output-dependent checks
            self.handle_no_output(rubric_items, compile_ok)

        # Phase 5: OOP practice
        oop_notes = self.check_oop_practices()

        # Build result
        result = GradingResult(
            student_name=self.student_name,
            student_id=self.student_id,
            rubric_items=rubric_items,
            compilation_success=compile_ok,
            execution_success=run_ok,
            actual_output=output,
            source_code=self.source_code,
            compiler_errors=compile_errors,
            oop_notes=oop_notes,
            expected_output=self.get_expected_output()
        )
        result.calculate_score()

        # Cleanup
        cleanup_temp_dir(self.work_dir)

        return result

    @abstractmethod
    def define_rubric(self) -> List[RubricItem]:
        """Return the list of rubric items for this assignment."""
        ...

    @abstractmethod
    def check_class_structure(self, items: List[RubricItem]):
        """Run AST-based checks on class structure."""
        ...

    @abstractmethod
    def check_output(self, items: List[RubricItem], output: str):
        """Verify program output against expected values."""
        ...

    def handle_no_output(self, items: List[RubricItem], compiled: bool):
        """Apply deductions when program can't be run."""
        for item in items:
            if item.category == "Main Method" and item.passed:
                if not compiled:
                    item.deduction = item.max_deduction
                    item.passed = False
                    item.notes = "Could not verify: compilation failed"
                else:
                    item.deduction = item.max_deduction
                    item.passed = False
                    item.notes = "Could not verify: runtime error"

    def get_expected_output(self) -> str:
        """Return expected output text for the report. Override per assignment."""
        return ""

    def check_oop_practices(self) -> List[str]:
        """Check for common OOP practice issues. Override for assignment-specific checks."""
        notes = []
        if not self.analyzer:
            return notes

        # Check for fields that should be private but aren't
        for f in self.analyzer.get_fields():
            if 'private' not in f.modifiers and f.name not in ('args',):
                if 'static' in f.modifiers and f.name == 'annualInterestRate':
                    continue  # Handled by rubric-specific check
                if 'public' in f.modifiers or not f.modifiers:
                    notes.append(f"Field '{f.name}' should be private")

        return notes
