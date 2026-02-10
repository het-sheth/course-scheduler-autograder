# Course Assignment Autograder - Claude Code Instructions

## Project Overview
Multi-assignment autograder for Java programming courses. Supports PA1-PA6 and a final project.
Each assignment has its own grader under `assignments/paX/` that inherits from `framework/base_grader.py`.

## Architecture
- `grade.py` - CLI entry point. Register new assignments in `ASSIGNMENT_GRADERS` dict.
- `framework/` - Reusable grading engine (submission handling, Java compile/run, AST analysis, HTML reports).
- `assignments/paX/` - Assignment-specific grading logic (rubric, AST checks, output checks, expected values).
- `assignments/final_project/` - Legacy Course Scheduler graders (standalone, not yet integrated into framework).

## Adding a New Assignment Grader
1. Create `assignments/paX/` directory with `__init__.py`.
2. Define rubric items in `rubric_items.py` (list of `RubricItem` objects).
3. Implement AST checks in `ast_checks.py` (class structure verification).
4. Implement output checks in `output_checks.py` (program output verification).
5. If needed, add `expected_values.py` with pre-computed expected output.
6. Create `grader.py` with `PAXGrader(BaseGrader)` overriding: `define_rubric()`, `check_class_structure()`, `check_output()`.
7. Register in `grade.py` ASSIGNMENT_GRADERS dict.

## Key Patterns
- **Deduction-based scoring**: Start at 100, subtract for each failed check. Defined per `RubricItem.max_deduction`.
- **AST-first, regex-fallback**: Use `javalang` AST parsing when possible, fall back to regex if parsing fails. See `framework/java_ast_analyzer.py`.
- **Package-aware compilation**: `framework/java_compiler.py` detects `package` declarations and sets up correct directory structure before `javac`.
- **Canvas filename parsing**: `framework/utils.py:parse_canvas_filename()` extracts student name, canvas ID, submission ID from Canvas download filenames.
- **Output verification**: Extract numbers from stdout, compare against pre-computed expected values. Tolerance = exact 2-decimal string match.

## Submission Formats Handled
- Canvas bulk download zip (zip of zips)
- Directory of individual student zips
- Single student zip
- NetBeans project structure (src/package/File.java)
- Raw .java files (no project structure)

## Git Commit Preferences
- Do NOT add Co-Authored-By lines to any commits.

## Dependencies
- `javalang` - Java AST parsing
- `jaydebeapi` - JDBC bridge (only needed for final project / Course Scheduler graders)
- Java JDK on PATH (javac, java)

## Running
```bash
python grade.py pa1 path/to/submissions/ --output report.html
```
