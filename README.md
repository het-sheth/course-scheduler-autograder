# Course Assignment Autograder

Automated grading system for Java programming course assignments. Grades student submissions downloaded from Canvas by analyzing Java source code (AST parsing) and verifying program output against expected values. Generates HTML reports with per-student score breakdowns.

## Supported Assignments

| Assignment | Description | Checks |
|------------|-------------|--------|
| `pa1` | Loan Account | Class structure, properties, constructor, methods, output formatting |
| `pa2` | Loan Account Hierarchy | Inheritance hierarchy, subclass structure, polymorphic output |
| `pa3` | Customer Loan Accounts | Customer class, ArrayList usage, printMonthlyReport, output verification |

## Quick Start

### Prerequisites

- Python 3.8+
- Java JDK on PATH (`javac`, `java`)

### Install

```bash
git clone https://github.com/het-sheth/course-scheduler-autograder.git
cd course-scheduler-autograder
pip install -r requirements.txt
```

### Grade Submissions

```bash
# Grade a directory of student zip files
python grade.py pa2 path/to/submissions/

# Grade with detailed per-rubric-item output
python grade.py pa2 path/to/submissions/ --verbose

# Custom output path for the HTML report
python grade.py pa3 path/to/submissions/ --output pa3_grades.html
```

### Input Formats

The grader accepts any of:

- **Directory of student `.zip` files** (Canvas bulk download extracted)
- **Canvas bulk download `.zip`** (zip of zips)
- **Single student `.zip`**

Student zips must contain a NetBeans project with a `src/` directory. Raw `.java` files without project structure are rejected.

## Project Structure

```
course-scheduler-autograder/
├── grade.py                      # CLI entry point
├── framework/                    # Reusable grading engine
│   ├── base_grader.py            #   Base class for all assignment graders
│   ├── submission_handler.py     #   Canvas zip extraction & discovery
│   ├── java_compiler.py          #   Package-aware javac/java wrapper
│   ├── java_ast_analyzer.py      #   javalang AST analysis helpers
│   ├── report_generator.py       #   HTML report generation
│   ├── rubric.py                 #   RubricItem / GradingResult models
│   └── utils.py                  #   Canvas filename parsing, temp dirs
├── assignments/                  # Assignment-specific graders
│   ├── pa1/
│   ├── pa2/
│   ├── pa3/
│   └── final_project/            #   Legacy Course Scheduler graders (standalone)
├── requirements.txt
└── LICENSE
```

## How Grading Works

1. **Discover** submissions from the input path (handles Canvas naming conventions).
2. **Extract** Java files from each student's zip, requiring NetBeans `src/` project structure.
3. **AST analysis** using `javalang` to verify class structure: properties, constructors, methods, inheritance, and method signatures. Falls back to regex if AST parsing fails.
4. **Compile and run** the Java code, capturing stdout.
5. **Output verification** against pre-computed expected values (exact 2-decimal string match for numeric output).
6. **Score** using deduction-based rubric: start at 100, subtract per failed check (capped by `max_deduction` per item).
7. **Generate** an HTML report with per-student breakdowns.

## Adding a New Assignment

1. Create `assignments/paX/` with `__init__.py`.
2. Define rubric in `rubric_items.py` (list of `RubricItem` objects).
3. Implement `ast_checks.py` for class structure verification.
4. Implement `output_checks.py` for program output verification.
5. Optionally add `expected_values.py` with pre-computed expected output.
6. Create `grader.py` with `PAXGrader(BaseGrader)` overriding `define_rubric()`, `check_class_structure()`, `check_output()`.
7. Register in `grade.py`'s `ASSIGNMENT_GRADERS` dict.

## Dependencies

- [`javalang`](https://github.com/c2nes/javalang) - Java AST parsing
- [`jaydebeapi`](https://github.com/baztian/jaydebeapi) - JDBC bridge (only needed for final project graders)

## License

MIT License - see [LICENSE](LICENSE) for details.
