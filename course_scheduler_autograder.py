#!/usr/bin/env python3
"""
Course Scheduler Final Project Auto-Grader
Automatically grades submissions for both Part 1 and Part 2
"""

import os
import sys
import zipfile
import shutil
import subprocess
import jaydebeapi
import re
from pathlib import Path
from datetime import datetime
import json

class CourseSchedulerGrader:
    def __init__(self, project_zip, database_zip, project_part=1):
        """
        Initialize the grader
        
        Args:
            project_zip: Path to the zipped NetBeans project
            database_zip: Path to the zipped Derby database
            project_part: 1 or 2 indicating which part to grade
        """
        self.project_zip = project_zip
        self.database_zip = database_zip
        self.project_part = project_part
        
        # Setup working directory
        self.work_dir = Path("/tmp/grading_workspace")
        self.work_dir.mkdir(exist_ok=True)
        
        # Grading results
        self.results = {
            "student_name": "",
            "timestamp": datetime.now().isoformat(),
            "part": project_part,
            "database_points": 0,
            "functionality_points": 0,
            "gui_points": 0,
            "code_quality_points": 0,
            "total_points": 0,
            "max_points": 100,
            "deductions": [],
            "comments": []
        }
        
        # Rubric point values
        self.setup_rubric()
    
    def setup_rubric(self):
        """Define rubric based on project part"""
        if self.project_part == 1:
            self.rubric = {
                "database": {
                    "tables_exist": 50,  # 10 per table
                    "correct_structure": 0,
                    "primary_keys": 0,
                    "empty_tables": 5
                },
                "functionality": {
                    "add_semester": 10,
                    "add_course": 10,
                    "add_class": 10,
                    "add_student": 10,
                    "display_classes": 10,
                    "schedule_class": 10,
                    "display_schedule": 10,
                    "waitlist_priority": 5
                },
                "gui": {
                    "combo_boxes": 5,
                    "auto_update": 3,
                    "display_results": 3
                },
                "code_quality": {
                    "prepared_statements": 10
                }
            }
        else:  # Part 2
            self.rubric = {
                "functionality": {
                    "display_class_list": 20,
                    "drop_class_db": 5,
                    "drop_class_schedule": 5,
                    "drop_class_display": 10,
                    "drop_class_combobox": 5,
                    "drop_student_db": 5,
                    "drop_student_semester": 5,
                    "drop_student_reschedule": 10,
                    "drop_student_waitlist": 5,
                    "drop_student_combobox": 5,
                    "student_drop_class_scheduled": 5,
                    "student_drop_class_waitlist_reschedule": 5,
                    "student_drop_class_waitlist_only": 5,
                    "waitlist_priority": 5
                },
                "gui": {
                    "combo_boxes": 5,
                    "auto_update": 3,
                    "display_results": 3
                },
                "code_quality": {
                    "prepared_statements": 10
                }
            }
    
    def extract_archives(self):
        """Extract both project and database archives"""
        print("Extracting submission files...")
        
        # Extract project
        self.project_dir = self.work_dir / "project"
        with zipfile.ZipFile(self.project_zip, 'r') as zip_ref:
            zip_ref.extractall(self.project_dir)
        
        # Extract database
        self.database_dir = self.work_dir / "database"
        with zipfile.ZipFile(self.database_zip, 'r') as zip_ref:
            zip_ref.extractall(self.database_dir)
        
        # Find actual project and database folders (handle nested folders)
        self.find_project_root()
        self.find_database_root()
        
        print(f"Project directory: {self.project_dir}")
        print(f"Database directory: {self.database_dir}")
    
    def find_project_root(self):
        """Find the root NetBeans project directory"""
        # Look for build.xml or src folder
        for root, dirs, files in os.walk(self.project_dir):
            if 'build.xml' in files or 'src' in dirs:
                self.project_dir = Path(root)
                return
        
        self.add_comment("WARNING: Could not find NetBeans project structure")
    
    def find_database_root(self):
        """Find the root Derby database directory"""
        # Look for log directory or service.properties
        for root, dirs, files in os.walk(self.database_dir):
            if 'log' in dirs or 'service.properties' in files:
                self.database_dir = Path(root)
                return
        
        self.add_comment("WARNING: Could not find Derby database structure")
    
    def validate_database(self):
        """Validate database structure and contents"""
        print("\n=== Validating Database Structure ===")
        
        try:
            # Connect to Derby database
            derby_jar = "/usr/share/java/derby.jar"  # Adjust path as needed
            if not os.path.exists(derby_jar):
                self.add_deduction(50, "Derby JAR not found - cannot validate database")
                return
            
            conn = jaydebeapi.connect(
                "org.apache.derby.jdbc.EmbeddedDriver",
                f"jdbc:derby:{self.database_dir}",
                ["java", "java"],
                derby_jar
            )
            
            cursor = conn.cursor()
            
            # Check required tables
            required_tables = ['SEMESTER', 'COURSES', 'CLASSES', 'STUDENTS', 'SCHEDULE']
            cursor.execute("SELECT TABLENAME FROM SYS.SYSTABLES WHERE TABLETYPE='T'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            missing_tables = [t for t in required_tables if t not in existing_tables]
            
            if missing_tables:
                deduction = len(missing_tables) * 10
                self.add_deduction(deduction, f"Missing tables: {', '.join(missing_tables)}")
            else:
                self.results["database_points"] += 50
                print("✓ All required tables exist")
            
            # Check if tables are empty
            tables_not_empty = []
            for table in required_tables:
                if table in existing_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        tables_not_empty.append(table)
            
            if tables_not_empty:
                self.add_deduction(5, f"Tables not empty: {', '.join(tables_not_empty)}")
            else:
                self.results["database_points"] += 5
                print("✓ All tables are empty as required")
            
            # Validate table structures
            self.validate_table_structures(cursor)
            
            conn.close()
            
        except Exception as e:
            self.add_deduction(50, f"Database validation error: {str(e)}")
            print(f"✗ Database error: {e}")
    
    def validate_table_structures(self, cursor):
        """Validate that tables have correct columns"""
        print("\nValidating table structures...")
        
        expected_structures = {
            'SEMESTER': ['SEMESTERTERM', 'SEMESTERYEAR'],
            'COURSES': ['COURSECODE', 'DESCRIPTION'],
            'CLASSES': ['SEMESTER', 'COURSECODE', 'SEATS'],
            'STUDENTS': ['STUDENTID', 'FIRSTNAME', 'LASTNAME'],
            'SCHEDULE': ['SEMESTER', 'COURSECODE', 'STUDENTID', 'STATUS', 'TIMESTAMP']
        }
        
        for table, expected_cols in expected_structures.items():
            try:
                cursor.execute(f"SELECT * FROM {table} WHERE 1=0")
                actual_cols = [desc[0] for desc in cursor.description]
                
                missing_cols = [col for col in expected_cols if col not in actual_cols]
                if missing_cols:
                    self.add_comment(f"Table {table} missing columns: {', '.join(missing_cols)}")
                else:
                    print(f"✓ Table {table} has correct structure")
            except:
                pass
    
    def analyze_code_quality(self):
        """Analyze source code for quality issues"""
        print("\n=== Analyzing Code Quality ===")
        
        src_dir = self.project_dir / "src"
        if not src_dir.exists():
            self.add_comment("Source directory not found")
            return
        
        java_files = list(src_dir.rglob("*.java"))
        print(f"Found {len(java_files)} Java files")
        
        # Check for PreparedStatements usage
        uses_prepared_statements = False
        uses_string_concatenation = False
        
        for java_file in java_files:
            content = java_file.read_text(errors='ignore')
            
            if 'PreparedStatement' in content:
                uses_prepared_statements = True
            
            # Check for SQL injection vulnerabilities (string concatenation in SQL)
            if re.search(r'executeUpdate\([^)]*\+', content) or \
               re.search(r'executeQuery\([^)]*\+', content):
                uses_string_concatenation = True
                self.add_comment(f"Possible SQL injection in {java_file.name}")
        
        if uses_prepared_statements:
            self.results["code_quality_points"] += 10
            print("✓ Uses PreparedStatements")
        else:
            self.add_deduction(10, "Does not use PreparedStatements")
        
        if uses_string_concatenation:
            self.add_deduction(5, "Uses string concatenation in SQL (security risk)")
    
    def run_functional_tests(self):
        """Run automated functional tests"""
        print("\n=== Running Functional Tests ===")
        print("Note: Full GUI testing requires manual verification")
        
        # This would require running the actual Java application
        # and simulating user interactions - complex automation
        
        self.add_comment("Functional tests require manual verification")
        self.add_comment("Please verify using the test script:")
        if self.project_part == 1:
            self.add_comment("- Add Semester functionality")
            self.add_comment("- Add Course functionality")
            self.add_comment("- Add Class functionality")
            self.add_comment("- Add Student functionality")
            self.add_comment("- Schedule Class functionality")
            self.add_comment("- Display Classes functionality")
            self.add_comment("- Display Schedule functionality")
        else:
            self.add_comment("- Display Class List functionality")
            self.add_comment("- Drop Student functionality")
            self.add_comment("- Drop Class functionality")
            self.add_comment("- Student Drop Class functionality")
    
    def check_naming_conventions(self):
        """Check if project and database follow naming conventions"""
        print("\n=== Checking Naming Conventions ===")
        
        # Project should be named CourseScheduler[Name][ID]
        project_name = self.project_dir.name
        if not project_name.startswith("CourseScheduler"):
            self.add_comment(f"Project name '{project_name}' doesn't follow naming convention")
        else:
            print(f"✓ Project name follows convention: {project_name}")
        
        # Extract student name from project name
        self.results["student_name"] = project_name
    
    def add_deduction(self, points, reason):
        """Record a point deduction"""
        self.results["deductions"].append({
            "points": points,
            "reason": reason
        })
        print(f"✗ -{points} pts: {reason}")
    
    def add_comment(self, comment):
        """Add a comment to the results"""
        self.results["comments"].append(comment)
        print(f"ℹ {comment}")
    
    def calculate_total_score(self):
        """Calculate final score"""
        total_deductions = sum(d["points"] for d in self.results["deductions"])
        
        self.results["total_points"] = self.results["max_points"] - total_deductions
        self.results["total_points"] += self.results.get("database_points", 0)
        self.results["total_points"] += self.results.get("functionality_points", 0)
        self.results["total_points"] += self.results.get("gui_points", 0)
        self.results["total_points"] += self.results.get("code_quality_points", 0)
        
        # Ensure score doesn't go below 0
        self.results["total_points"] = max(0, self.results["total_points"])
    
    def generate_report(self):
        """Generate grading report"""
        print("\n" + "="*60)
        print("GRADING REPORT")
        print("="*60)
        print(f"Student: {self.results['student_name']}")
        print(f"Part: {self.results['part']}")
        print(f"Date: {self.results['timestamp']}")
        print("="*60)
        
        print(f"\nDatabase Structure: {self.results.get('database_points', 0)} pts")
        print(f"Functionality: {self.results.get('functionality_points', 0)} pts (manual verification needed)")
        print(f"GUI: {self.results.get('gui_points', 0)} pts (manual verification needed)")
        print(f"Code Quality: {self.results.get('code_quality_points', 0)} pts")
        
        print(f"\nDeductions:")
        for deduction in self.results['deductions']:
            print(f"  -{deduction['points']} pts: {deduction['reason']}")
        
        print(f"\nComments:")
        for comment in self.results['comments']:
            print(f"  • {comment}")
        
        print("="*60)
        print(f"TOTAL SCORE: {self.results['total_points']}/{self.results['max_points']}")
        print("="*60)
        
        # Save report to file
        report_file = self.work_dir / "grading_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nReport saved to: {report_file}")
        
        return report_file
    
    def grade(self):
        """Main grading workflow"""
        print("Course Scheduler Auto-Grader")
        print(f"Grading Part {self.project_part}")
        print("="*60)
        
        try:
            # Extract files
            self.extract_archives()
            
            # Check naming conventions
            self.check_naming_conventions()
            
            # Validate database
            self.validate_database()
            
            # Analyze code quality
            self.analyze_code_quality()
            
            # Run functional tests (limited automation)
            self.run_functional_tests()
            
            # Calculate score
            self.calculate_total_score()
            
            # Generate report
            report_file = self.generate_report()
            
            return report_file
            
        except Exception as e:
            print(f"\nGRADING ERROR: {e}")
            import traceback
            traceback.print_exc()
            return None


def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: python course_scheduler_autograder.py <project.zip> <database.zip> [part]")
        print("  part: 1 or 2 (default: 1)")
        sys.exit(1)
    
    project_zip = sys.argv[1]
    database_zip = sys.argv[2]
    part = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    
    if not os.path.exists(project_zip):
        print(f"Error: Project file not found: {project_zip}")
        sys.exit(1)
    
    if not os.path.exists(database_zip):
        print(f"Error: Database file not found: {database_zip}")
        sys.exit(1)
    
    grader = CourseSchedulerGrader(project_zip, database_zip, part)
    report_file = grader.grade()
    
    if report_file:
        print(f"\n✓ Grading complete! Report saved to: {report_file}")
    else:
        print("\n✗ Grading failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
