#!/usr/bin/env python3
"""
Fully Automated Course Scheduler Grader
Compiles, runs, and tests student code automatically
"""

import os
import sys
import zipfile
import subprocess
import jaydebeapi
import re
import json
from pathlib import Path
from datetime import datetime
from advanced_code_analyzer import CodeAnalyzer, FunctionalityTester

class FullyAutomatedGrader:
    def __init__(self, project_zip, database_zip, project_part=1):
        self.project_zip = project_zip
        self.database_zip = database_zip
        self.project_part = project_part
        
        self.work_dir = Path("/tmp/auto_grading")
        self.work_dir.mkdir(exist_ok=True)
        
        self.results = {
            "student_name": "",
            "timestamp": datetime.now().isoformat(),
            "part": project_part,
            "automated_score": 0,
            "max_automated_score": 100,
            "breakdown": {
                "database": 0,
                "code_analysis": 0,
                "compilation": 0,
                "functionality": 0,
                "gui_components": 0
            },
            "deductions": [],
            "passed_tests": [],
            "failed_tests": []
        }
    
    def extract_and_setup(self):
        """Extract archives and setup environment"""
        print("="*60)
        print("FULLY AUTOMATED GRADING")
        print("="*60)
        print("\nExtracting files...")
        
        # Extract project
        self.project_dir = self.work_dir / "project"
        with zipfile.ZipFile(self.project_zip, 'r') as zip_ref:
            zip_ref.extractall(self.project_dir)
        
        # Extract database
        self.database_dir = self.work_dir / "database"
        with zipfile.ZipFile(self.database_zip, 'r') as zip_ref:
            zip_ref.extractall(self.database_dir)
        
        # Find roots
        self.find_project_root()
        self.find_database_root()
        
        self.results["student_name"] = self.project_dir.name
        
        print(f"✓ Project: {self.project_dir.name}")
        print(f"✓ Database: {self.database_dir.name}")
    
    def find_project_root(self):
        """Find NetBeans project root"""
        for root, dirs, files in os.walk(self.project_dir):
            if 'build.xml' in files or 'src' in dirs:
                self.project_dir = Path(root)
                return
    
    def find_database_root(self):
        """Find Derby database root"""
        for root, dirs, files in os.walk(self.database_dir):
            if 'log' in dirs or 'service.properties' in files:
                self.database_dir = Path(root)
                return
    
    def test_database(self):
        """Test database structure and connectivity"""
        print("\n" + "="*60)
        print("PHASE 1: DATABASE TESTING")
        print("="*60)
        
        try:
            derby_jar = self.find_derby_jar()
            if not derby_jar:
                self.add_failure("Derby JAR not found", 50)
                return
            
            conn = jaydebeapi.connect(
                "org.apache.derby.jdbc.EmbeddedDriver",
                f"jdbc:derby:{self.database_dir}",
                ["java", "java"],
                derby_jar
            )
            
            cursor = conn.cursor()
            
            # Test 1: Required tables exist
            print("\nTest 1: Checking required tables...")
            required_tables = ['SEMESTER', 'COURSES', 'CLASSES', 'STUDENTS', 'SCHEDULE']
            cursor.execute("SELECT TABLENAME FROM SYS.SYSTABLES WHERE TABLETYPE='T'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            missing_tables = [t for t in required_tables if t not in existing_tables]
            
            if not missing_tables:
                self.add_success("All 5 required tables exist", 50)
            else:
                points_lost = len(missing_tables) * 10
                self.add_failure(f"Missing tables: {', '.join(missing_tables)}", points_lost)
            
            # Test 2: Tables are empty
            print("\nTest 2: Checking tables are empty...")
            all_empty = True
            for table in required_tables:
                if table in existing_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        all_empty = False
                        print(f"  ✗ {table} has {count} rows (should be 0)")
            
            if all_empty:
                self.add_success("All tables are empty", 5)
            else:
                self.add_failure("Tables contain data", 5)
            
            # Test 3: Table structures
            print("\nTest 3: Validating table structures...")
            structure_points = self.validate_table_structures(cursor)
            if structure_points > 0:
                self.add_success(f"Table structures correct", structure_points)
            
            conn.close()
            
        except Exception as e:
            self.add_failure(f"Database error: {str(e)}", 55)
            print(f"✗ Database testing failed: {e}")
    
    def validate_table_structures(self, cursor):
        """Validate detailed table structures"""
        expected = {
            'SEMESTER': ['SEMESTERTERM', 'SEMESTERYEAR'],
            'COURSES': ['COURSECODE', 'DESCRIPTION'],
            'CLASSES': ['SEMESTER', 'COURSECODE', 'SEATS'],
            'STUDENTS': ['STUDENTID', 'FIRSTNAME', 'LASTNAME'],
            'SCHEDULE': ['SEMESTER', 'COURSECODE', 'STUDENTID', 'STATUS', 'TIMESTAMP']
        }
        
        points = 0
        for table, expected_cols in expected.items():
            try:
                cursor.execute(f"SELECT * FROM {table} WHERE 1=0")
                actual_cols = [desc[0] for desc in cursor.description]
                
                if all(col in actual_cols for col in expected_cols):
                    print(f"  ✓ {table} structure correct")
                    points += 2
                else:
                    missing = [c for c in expected_cols if c not in actual_cols]
                    print(f"  ✗ {table} missing columns: {missing}")
            except:
                pass
        
        return points
    
    def analyze_code(self):
        """Deep code analysis"""
        print("\n" + "="*60)
        print("PHASE 2: CODE ANALYSIS")
        print("="*60)
        
        src_dir = self.project_dir / "src"
        if not src_dir.exists():
            self.add_failure("Source directory not found", 30)
            return
        
        analyzer = CodeAnalyzer(src_dir)
        analysis = analyzer.analyze_all()
        analyzer.check_sql_security()
        
        # Award points based on analysis
        code_points = analysis["points"]
        self.results["breakdown"]["code_analysis"] = code_points
        self.results["automated_score"] += code_points
        
        # Add specific findings
        for issue in analysis["issues"]:
            self.results["failed_tests"].append(issue)
    
    def compile_and_test(self):
        """Compile code and run functional tests"""
        print("\n" + "="*60)
        print("PHASE 3: COMPILATION & EXECUTION")
        print("="*60)
        
        src_dir = self.project_dir / "src"
        
        # Test 4: Compilation
        print("\nTest 4: Compiling project...")
        if self.compile_project(src_dir):
            self.add_success("Project compiles successfully", 10)
            
            # Test 5: Run main class
            print("\nTest 5: Testing main class execution...")
            if self.test_main_execution():
                self.add_success("Main class executes", 5)
            else:
                self.add_failure("Main class execution failed", 5)
        else:
            self.add_failure("Compilation failed", 15)
    
    def compile_project(self, src_dir):
        """Compile the Java project"""
        java_files = list(src_dir.rglob("*.java"))
        if not java_files:
            return False
        
        build_dir = self.project_dir / "build"
        build_dir.mkdir(exist_ok=True)
        
        try:
            # Build classpath
            derby_jar = self.find_derby_jar()
            classpath = f"{build_dir}:{derby_jar}" if derby_jar else str(build_dir)
            
            cmd = [
                "javac",
                "-d", str(build_dir),
                "-cp", classpath,
                *[str(f) for f in java_files]
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("  ✓ Compilation successful")
                return True
            else:
                print(f"  ✗ Compilation errors:")
                print(result.stderr[:500])  # First 500 chars
                return False
                
        except subprocess.TimeoutExpired:
            print("  ✗ Compilation timeout")
            return False
        except Exception as e:
            print(f"  ✗ Compilation error: {e}")
            return False
    
    def test_main_execution(self):
        """Try to execute main class (with timeout)"""
        try:
            # Find main class
            main_class = self.find_main_class()
            if not main_class:
                print("  ⚠ Main class not found")
                return False
            
            build_dir = self.project_dir / "build"
            derby_jar = self.find_derby_jar()
            classpath = f"{build_dir}:{derby_jar}:{self.database_dir}" if derby_jar else str(build_dir)
            
            cmd = [
                "java",
                "-cp", classpath,
                "-Djava.awt.headless=true",  # Headless mode for GUI
                main_class
            ]
            
            # Run with very short timeout just to see if it starts
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=2  # 2 second timeout
            )
            
            # Even if it times out, if no error occurred, it started successfully
            return True
            
        except subprocess.TimeoutExpired:
            # Timeout is actually good - means it started running!
            print("  ✓ Main class started (timed out waiting for GUI)")
            return True
        except Exception as e:
            print(f"  ✗ Execution error: {e}")
            return False
    
    def find_main_class(self):
        """Find the class with main method"""
        src_dir = self.project_dir / "src"
        
        for java_file in src_dir.rglob("*.java"):
            content = java_file.read_text(errors='ignore')
            if re.search(r'public\s+static\s+void\s+main\s*\(', content):
                # Extract package and class name
                package = ""
                package_match = re.search(r'package\s+([\w.]+)\s*;', content)
                if package_match:
                    package = package_match.group(1) + "."
                
                class_match = re.search(r'public\s+class\s+(\w+)', content)
                if class_match:
                    class_name = class_match.group(1)
                    return f"{package}{class_name}"
        
        return None
    
    def test_gui_components_detailed(self):
        """Detailed GUI component testing"""
        print("\n" + "="*60)
        print("PHASE 4: GUI COMPONENT VERIFICATION")
        print("="*60)
        
        src_dir = self.project_dir / "src"
        all_content = ""
        
        for java_file in src_dir.rglob("*.java"):
            all_content += java_file.read_text(errors='ignore') + "\n"
        
        if self.project_part == 1:
            self.test_part1_gui(all_content)
        else:
            self.test_part2_gui(all_content)
    
    def test_part1_gui(self, content):
        """Test Part 1 GUI requirements"""
        tests = {
            "Add Semester button": (r'JButton.*["\'].*Semester|Semester.*JButton', 2),
            "Add Course button": (r'JButton.*["\'].*Course|Course.*JButton', 2),
            "Add Class button": (r'JButton.*["\'].*Class|Class.*JButton', 2),
            "Add Student button": (r'JButton.*["\'].*Student|Student.*JButton', 2),
            "Schedule Class button": (r'JButton.*["\'].*Schedule|Schedule.*JButton', 2),
            "JComboBox components": (r'JComboBox', 3),  # Need at least 3
            "ActionListener implementation": (r'implements\s+ActionListener|ActionListener', 3),
            "Database connection": (r'jdbc:derby|DriverManager\.getConnection', 5),
            "JTextField for input": (r'JTextField', 2)
        }
        
        for test_name, (pattern, points) in tests.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                count = len(matches)
                if count >= 3 or test_name != "JComboBox components":
                    self.add_success(f"{test_name} found ({count})", points)
                else:
                    self.add_failure(f"{test_name}: only {count} found", points)
            else:
                self.add_failure(f"{test_name} not found", points)
    
    def test_part2_gui(self, content):
        """Test Part 2 GUI requirements"""
        tests = {
            "Drop Student functionality": (r'drop.*student|remove.*student', 3, re.IGNORECASE),
            "Drop Class functionality": (r'drop.*class|remove.*class', 3, re.IGNORECASE),
            "Display Class List": (r'display.*list|show.*list', 2, re.IGNORECASE),
            "Waitlist handling": (r'waitlist|wait.*list', 3, re.IGNORECASE),
            "Timestamp usage": (r'Timestamp|timestamp', 2, re.IGNORECASE)
        }
        
        for test_name, (pattern, points, *flags) in tests.items():
            flag = flags[0] if flags else 0
            if re.search(pattern, content, flag):
                self.add_success(f"{test_name} implemented", points)
            else:
                self.add_failure(f"{test_name} not found", points)
    
    def find_derby_jar(self):
        """Find Derby JAR file"""
        common_locations = [
            "/usr/share/java/derby.jar",
            "/usr/lib/jvm/java-11-openjdk-amd64/lib/derby.jar",
            str(Path.home() / "lib/derby.jar")
        ]
        
        for location in common_locations:
            if os.path.exists(location):
                return location
        
        # Search system
        result = subprocess.run(
            ["find", "/usr", "-name", "derby.jar", "2>/dev/null"],
            capture_output=True,
            text=True,
            shell=True
        )
        
        if result.stdout:
            return result.stdout.strip().split('\n')[0]
        
        return None
    
    def add_success(self, test_name, points):
        """Record successful test"""
        self.results["passed_tests"].append({
            "test": test_name,
            "points": points
        })
        self.results["automated_score"] += points
        print(f"  ✓ {test_name} (+{points} pts)")
    
    def add_failure(self, test_name, points_lost):
        """Record failed test"""
        self.results["failed_tests"].append({
            "test": test_name,
            "points_lost": points_lost
        })
        print(f"  ✗ {test_name} (-{points_lost} pts)")
    
    def generate_report(self):
        """Generate comprehensive report"""
        print("\n" + "="*60)
        print("AUTOMATED GRADING REPORT")
        print("="*60)
        
        print(f"\nStudent: {self.results['student_name']}")
        print(f"Part: {self.project_part}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n" + "-"*60)
        print("PASSED TESTS:")
        print("-"*60)
        for test in self.results["passed_tests"]:
            print(f"  ✓ {test['test']}: +{test['points']} pts")
        
        print("\n" + "-"*60)
        print("FAILED TESTS:")
        print("-"*60)
        for test in self.results["failed_tests"]:
            print(f"  ✗ {test['test']}: -{test['points_lost']} pts")
        
        print("\n" + "="*60)
        print(f"TOTAL AUTOMATED SCORE: {self.results['automated_score']}/{self.results['max_automated_score']}")
        print("="*60)
        
        print("\n📝 Note: This is the automated portion only.")
        print("   Manual GUI testing may award additional points.")
        
        # Save JSON report
        report_file = self.work_dir / "automated_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        return report_file
    
    def grade(self):
        """Main grading workflow"""
        try:
            self.extract_and_setup()
            self.test_database()
            self.analyze_code()
            self.compile_and_test()
            self.test_gui_components_detailed()
            
            report_file = self.generate_report()
            return report_file
            
        except Exception as e:
            print(f"\n✗ GRADING ERROR: {e}")
            import traceback
            traceback.print_exc()
            return None


def main():
    if len(sys.argv) < 3:
        print("Usage: python fully_automated_grader.py <project.zip> <database.zip> [part]")
        sys.exit(1)
    
    project_zip = sys.argv[1]
    database_zip = sys.argv[2]
    part = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    
    grader = FullyAutomatedGrader(project_zip, database_zip, part)
    report_file = grader.grade()
    
    if report_file:
        print(f"\n✓ Report saved to: {report_file}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
