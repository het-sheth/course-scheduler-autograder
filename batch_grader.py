#!/usr/bin/env python3
"""
Batch Grader for Course Scheduler Final Project
Processes multiple student submissions and generates comparative reports
"""

import os
import sys
from pathlib import Path
import json
import csv
from datetime import datetime
from course_scheduler_autograder import CourseSchedulerGrader

class BatchGrader:
    def __init__(self, submissions_dir, output_dir, project_part=1):
        """
        Initialize batch grader
        
        Args:
            submissions_dir: Directory containing student submissions
            output_dir: Directory for grading reports
            project_part: 1 or 2
        """
        self.submissions_dir = Path(submissions_dir)
        self.output_dir = Path(output_dir)
        self.project_part = project_part
        
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        self.all_results = []
    
    def find_submissions(self):
        """
        Find all student submissions
        Expected structure:
          submissions/
            StudentName1/
              project.zip
              database.zip
            StudentName2/
              project.zip
              database.zip
        """
        submissions = []
        
        for student_dir in self.submissions_dir.iterdir():
            if not student_dir.is_dir():
                continue
            
            # Look for project and database zips
            project_files = list(student_dir.glob("*project*.zip")) + \
                          list(student_dir.glob("CourseScheduler*.zip"))
            db_files = list(student_dir.glob("*database*.zip")) + \
                      list(student_dir.glob("*DB*.zip"))
            
            if project_files and db_files:
                submissions.append({
                    'student': student_dir.name,
                    'project_zip': project_files[0],
                    'database_zip': db_files[0]
                })
            else:
                print(f"⚠ Incomplete submission for {student_dir.name}")
        
        return submissions
    
    def grade_all(self):
        """Grade all submissions"""
        submissions = self.find_submissions()
        
        print(f"\nFound {len(submissions)} submissions to grade")
        print("="*60)
        
        for i, submission in enumerate(submissions, 1):
            print(f"\n[{i}/{len(submissions)}] Grading {submission['student']}...")
            print("-"*60)
            
            try:
                grader = CourseSchedulerGrader(
                    submission['project_zip'],
                    submission['database_zip'],
                    self.project_part
                )
                
                report_file = grader.grade()
                
                # Load results
                with open(report_file) as f:
                    results = json.load(f)
                
                results['student'] = submission['student']
                self.all_results.append(results)
                
                # Copy report to output directory
                student_report = self.output_dir / f"{submission['student']}_report.json"
                with open(student_report, 'w') as f:
                    json.dump(results, f, indent=2)
                
                print(f"✓ Completed: {results['total_points']}/{results['max_points']}")
                
            except Exception as e:
                print(f"✗ Error grading {submission['student']}: {e}")
                self.all_results.append({
                    'student': submission['student'],
                    'total_points': 0,
                    'max_points': 100,
                    'error': str(e)
                })
        
        # Generate summary report
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate summary CSV and statistics"""
        print("\n" + "="*60)
        print("GENERATING SUMMARY REPORT")
        print("="*60)
        
        # Create CSV report
        csv_file = self.output_dir / f"grading_summary_part{self.project_part}.csv"
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Student',
                'Total Points',
                'Max Points',
                'Percentage',
                'Database Points',
                'Code Quality Points',
                'Major Issues'
            ])
            
            for result in sorted(self.all_results, key=lambda x: x.get('student', '')):
                student = result.get('student', 'Unknown')
                total = result.get('total_points', 0)
                max_pts = result.get('max_points', 100)
                percentage = (total / max_pts * 100) if max_pts > 0 else 0
                
                db_pts = result.get('database_points', 0)
                code_pts = result.get('code_quality_points', 0)
                
                # Summarize major issues
                major_issues = []
                for deduction in result.get('deductions', []):
                    if deduction['points'] >= 10:
                        major_issues.append(f"{deduction['reason']} (-{deduction['points']})")
                
                issues_str = '; '.join(major_issues) if major_issues else 'None'
                
                writer.writerow([
                    student,
                    total,
                    max_pts,
                    f"{percentage:.1f}%",
                    db_pts,
                    code_pts,
                    issues_str
                ])
        
        print(f"✓ CSV report saved: {csv_file}")
        
        # Calculate statistics
        scores = [r.get('total_points', 0) for r in self.all_results]
        if scores:
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)
            
            print(f"\nStatistics:")
            print(f"  Students graded: {len(scores)}")
            print(f"  Average score: {avg_score:.1f}")
            print(f"  Highest score: {max_score}")
            print(f"  Lowest score: {min_score}")
        
        # Generate detailed HTML report
        self.generate_html_report()
    
    def generate_html_report(self):
        """Generate HTML summary report"""
        html_file = self.output_dir / f"grading_summary_part{self.project_part}.html"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Course Scheduler Part {self.project_part} - Grading Summary</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #003366; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #003366; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .score-high {{ color: green; font-weight: bold; }}
        .score-medium {{ color: orange; font-weight: bold; }}
        .score-low {{ color: red; font-weight: bold; }}
        .stats {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>Course Scheduler Final Project - Part {self.project_part}</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="stats">
        <h2>Summary Statistics</h2>
        <p><strong>Total Submissions:</strong> {len(self.all_results)}</p>
"""
        
        scores = [r.get('total_points', 0) for r in self.all_results]
        if scores:
            html_content += f"""
        <p><strong>Average Score:</strong> {sum(scores)/len(scores):.1f} / 100</p>
        <p><strong>Highest Score:</strong> {max(scores)}</p>
        <p><strong>Lowest Score:</strong> {min(scores)}</p>
"""
        
        html_content += """
    </div>
    
    <h2>Detailed Results</h2>
    <table>
        <tr>
            <th>Student</th>
            <th>Total Score</th>
            <th>Percentage</th>
            <th>Database</th>
            <th>Code Quality</th>
            <th>Major Issues</th>
        </tr>
"""
        
        for result in sorted(self.all_results, key=lambda x: x.get('total_points', 0), reverse=True):
            student = result.get('student', 'Unknown')
            total = result.get('total_points', 0)
            max_pts = result.get('max_points', 100)
            percentage = (total / max_pts * 100) if max_pts > 0 else 0
            
            # Color code based on percentage
            if percentage >= 90:
                score_class = "score-high"
            elif percentage >= 70:
                score_class = "score-medium"
            else:
                score_class = "score-low"
            
            db_pts = result.get('database_points', 0)
            code_pts = result.get('code_quality_points', 0)
            
            # List major deductions
            major_issues = []
            for deduction in result.get('deductions', []):
                if deduction['points'] >= 10:
                    major_issues.append(deduction['reason'])
            
            issues_html = '<br>'.join(major_issues) if major_issues else 'None'
            
            html_content += f"""
        <tr>
            <td>{student}</td>
            <td class="{score_class}">{total} / {max_pts}</td>
            <td class="{score_class}">{percentage:.1f}%</td>
            <td>{db_pts}</td>
            <td>{code_pts}</td>
            <td>{issues_html}</td>
        </tr>
"""
        
        html_content += """
    </table>
</body>
</html>
"""
        
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        print(f"✓ HTML report saved: {html_file}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python batch_grader.py <submissions_dir> <output_dir> [part]")
        print("  part: 1 or 2 (default: 1)")
        sys.exit(1)
    
    submissions_dir = sys.argv[1]
    output_dir = sys.argv[2]
    part = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    
    grader = BatchGrader(submissions_dir, output_dir, part)
    grader.grade_all()
    
    print("\n✓ Batch grading complete!")


if __name__ == "__main__":
    main()
