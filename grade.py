#!/usr/bin/env python3
"""
Course Assignment Autograder - Main CLI Entry Point.

Usage:
    python grade.py pa1 <path_to_submissions> [--output report.html]

Supports:
    - A directory of individual student .zip files
    - A single Canvas bulk download .zip
    - A single student .zip file
"""

import argparse
import sys
from pathlib import Path

from framework.submission_handler import SubmissionHandler
from framework.report_generator import HTMLReportGenerator
from framework.rubric import GradingResult


ASSIGNMENT_GRADERS = {
    'pa1': ('assignments.pa1.grader', 'PA1Grader'),
    'pa2': ('assignments.pa2.grader', 'PA2Grader'),
    # Future assignments:
    # 'pa3': ('assignments.pa3.grader', 'PA3Grader'),
    # 'pa4': ('assignments.pa4.grader', 'PA4Grader'),
    # 'pa5': ('assignments.pa5.grader', 'PA5Grader'),
    # 'pa6': ('assignments.pa6.grader', 'PA6Grader'),
    # 'final': ('assignments.final_project.grader', 'FinalProjectGrader'),
}

ASSIGNMENT_NAMES = {
    'pa1': 'PA1 - Loan Account',
    'pa2': 'PA2 - Loan Account Hierarchy',
}


def load_grader_class(assignment: str):
    """Dynamically import the grader class for the given assignment."""
    module_path, class_name = ASSIGNMENT_GRADERS[assignment]
    module = __import__(module_path, fromlist=[class_name])
    return getattr(module, class_name)


def main():
    parser = argparse.ArgumentParser(
        description='Course Assignment Autograder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python grade.py pa1 ./submissions/pa1/
  python grade.py pa1 ./submissions/pa1/ --output pa1_grades.html
  python grade.py pa1 ./student_submission.zip
  python grade.py pa1 ./canvas_bulk_download.zip"""
    )
    parser.add_argument('assignment', choices=ASSIGNMENT_GRADERS.keys(),
                        help='Assignment to grade')
    parser.add_argument('input_path', type=Path,
                        help='Path to submissions directory, bulk zip, or single student zip')
    parser.add_argument('--output', '-o', type=Path, default=None,
                        help='Output HTML report path (default: <assignment>_report.html)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed grading output')

    args = parser.parse_args()

    if not args.input_path.exists():
        print(f"Error: Input path does not exist: {args.input_path}")
        sys.exit(1)

    # Load grader
    GraderClass = load_grader_class(args.assignment)
    display_name = ASSIGNMENT_NAMES.get(args.assignment, args.assignment.upper())

    print(f"{'='*60}")
    print(f"  Autograder: {display_name}")
    print(f"  Input: {args.input_path}")
    print(f"{'='*60}")

    # Discover submissions
    handler = SubmissionHandler(args.input_path)
    submissions = handler.discover_submissions()

    if not submissions:
        print("No submissions found.")
        sys.exit(1)

    print(f"\nFound {len(submissions)} submission(s)\n")

    # Grade each submission
    results = []
    for i, sub in enumerate(submissions, 1):
        print(f"[{i}/{len(submissions)}] Grading: {sub.student_name}...", end=" ")

        if sub.error:
            print(f"SKIP ({sub.error})")
            result = GradingResult(
                student_name=sub.student_name,
                student_id=sub.canvas_id,
                total_score=0,
                error_message=sub.error
            )
            results.append(result)
            continue

        # Extract java files
        java_files = handler.extract_java_files(sub)

        if not java_files:
            print(f"SKIP ({sub.error or 'No Java files found'})")
            result = GradingResult(
                student_name=sub.student_name,
                student_id=sub.canvas_id,
                total_score=0,
                error_message=sub.error or "No Java files found in submission"
            )
            results.append(result)
            continue

        try:
            grader = GraderClass(java_files, sub.student_name, sub.canvas_id)
            result = grader.grade()
            results.append(result)
            print(f"{result.total_score}/100 ({result.letter_grade})")

            if args.verbose:
                for item in result.rubric_items:
                    status = "PASS" if item.passed else "FAIL"
                    print(f"    [{status}] {item.description} ({'-' + str(item.deduction) if item.deduction else 'OK'})")
                if result.oop_notes:
                    for note in result.oop_notes:
                        print(f"    [OOP] {note}")
                print()

        except Exception as e:
            print(f"ERROR ({e})")
            result = GradingResult(
                student_name=sub.student_name,
                student_id=sub.canvas_id,
                total_score=0,
                error_message=str(e)
            )
            results.append(result)

    # Generate report
    output_path = args.output or Path(f"{args.assignment}_report.html")
    reporter = HTMLReportGenerator(display_name, results)
    reporter.generate(output_path)

    # Console summary
    print(f"\n{'='*60}")
    print(f"  GRADING COMPLETE")
    print(f"{'='*60}")
    print(f"  Students graded: {len(results)}")
    if results:
        scores = [r.total_score for r in results]
        print(f"  Average score: {sum(scores)/len(scores):.1f}/100")
        print(f"  High: {max(scores)}/100  Low: {min(scores)}/100")
    print(f"  Report: {output_path.resolve()}")
    print(f"{'='*60}")

    # Cleanup
    handler.cleanup()

    return 0


if __name__ == '__main__':
    sys.exit(main())
