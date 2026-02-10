#!/usr/bin/env python3
"""
ULTIMATE 100% AUTOMATED GRADER (Windows Compatible)
Combines everything: database, code, compilation, AND test script execution
ZERO human intervention required!
"""
import os
import sys
import zipfile
import subprocess
import jaydebeapi
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Import our other components
from fully_automated_grader import FullyAutomatedGrader
from test_script_executor import TestScriptExecutor

# ========================================
# CRITICAL: Initialize JVM with Derby JAR
# ========================================
import jpype

def initialize_jvm_with_derby():
    """Initialize JVM and add Derby JAR to classpath"""
    if jpype.isJVMStarted():
        return True
    
    if not os.environ.get('JAVA_HOME'):
        os.environ['JAVA_HOME'] = r'C:\Program Files\Java\jdk-21'
    
    derby_jar = r"C:\Derby\lib\derby.jar"
    if not os.path.exists(derby_jar):
        return False
    
    try:
        jvm_path = os.path.join(os.environ['JAVA_HOME'], 'bin', 'server', 'jvm.dll')
        if os.path.exists(jvm_path):
            jpype.startJVM(jvm_path, convertStrings=False)
            jpype.addClassPath(derby_jar)
            return True
    except:
        return False

# Initialize JVM when module loads
initialize_jvm_with_derby()
# ========================================

class UltimateAutomatedGrader:
    """
    The ultimate grader that does EVERYTHING:
    1. Database validation (55 pts)
    2. Code analysis (20 pts)
    3. Compilation (10 pts)
    4. Test script execution (15 pts) 
    
    Total: 100 pts fully automated!
    """
    
    def __init__(self, project_zip, database_zip, project_part=1):
        self.project_zip = project_zip
        self.database_zip = database_zip
        self.project_part = project_part
        
        # Use Windows-compatible temp directory
        if sys.platform == "win32":
            # Use Windows temp directory
            temp_base = Path(tempfile.gettempdir()) / "ultimate_grading"
        else:
            # Use /tmp on Unix systems
            temp_base = Path("/tmp/ultimate_grading")
        
        self.work_dir = temp_base
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        self.final_results = {
            "student_name": "",
            "timestamp": datetime.now().isoformat(),
            "part": project_part,
            "phase_scores": {
                "database": 0,
                "code_analysis": 0,
                "compilation": 0,
                "functionality": 0
            },
            "total_score": 0,
            "max_score": 100,
            "grade_letter": "",
            "summary": []
        }
    
    def grade_everything(self):
        """Execute all grading phases"""
        print("="*80)
        print(" "*20 + "ULTIMATE AUTOMATED GRADER")
        print(" "*15 + "100% AUTOMATED - ZERO HUMAN INTERVENTION")
        print("="*80)
        
        # Phase 1: Structural Analysis
        print("\n" + "█"*80)
        print("PHASE 1: STRUCTURAL ANALYSIS (Database + Code)")
        print("█"*80)
        
        grader = FullyAutomatedGrader(self.project_zip, self.database_zip, self.project_part)
        structural_report = grader.grade()
        
        if structural_report:
            with open(structural_report) as f:
                structural_data = json.load(f)
            
            self.final_results["student_name"] = structural_data.get("student_name", "Unknown")
            
            # --- MISSING LINE ADDED HERE ---
            total_phase1 = structural_data.get("automated_score", 0)
            # -------------------------------

            # Extract actual scores from passed tests
            passed_tests = structural_data.get("passed_tests", [])
            
            db_score = 0
            compile_score = 0
            gui_score = 0
            
            for test in passed_tests:
                test_name = test.get("test", "").lower()
                points = test.get("points", 0)
                
                # Categorize by keywords
                if any(k in test_name for k in ["table", "empty", "structure"]):
                    db_score += points
                elif any(k in test_name for k in ["compil", "execute", "main"]):
                    compile_score += points
                elif any(k in test_name for k in ["drop", "display", "waitlist", "timestamp"]):
                    gui_score += points
            
            # Code analysis is everything else
            code_score = total_phase1 - db_score - compile_score - gui_score
            
            self.final_results["phase_scores"]["database"] = min(db_score, 55)
            
            # --- LENIENT GRADING SCHEME ---
            # If the project compiles (10 pts) and runs (5 pts), guarantee at least 15/20 for code quality.
            # This treats missing classes/patterns as minor style deductions (-5 max).
            if compile_score >= 10: 
                self.final_results["phase_scores"]["code_analysis"] = max(15, min(code_score, 20))
            else:
                self.final_results["phase_scores"]["code_analysis"] = min(code_score, 20)
            # ------------------------------

            self.final_results["phase_scores"]["compilation"] = min(compile_score + gui_score, 10)
            
            print(f"\n✓ Phase 1 Complete")
            print(f"  Database: {self.final_results['phase_scores']['database']} pts")
            print(f"  Code Analysis: {self.final_results['phase_scores']['code_analysis']} pts")
            print(f"  Compilation: {self.final_results['phase_scores']['compilation']} pts")
        
        # Phase 2: Functional Testing
        print("\n" + "█"*80)
        print("PHASE 2: FUNCTIONAL TESTING (Test Script Execution)")
        print("█"*80)
        
        database_dir = self.find_extracted_database()
        
        if database_dir:
            executor = TestScriptExecutor(database_dir, self.project_part)
            
            try:
                # Clear database first (tests expect empty DB)
                self.clear_database(database_dir)
                
                executor.connect_database()
                
                if self.project_part == 1:
                    executor.run_part1_tests()
                else:
                    executor.run_part2_tests()
                
                executor.cleanup()
                
                # Get test results
                functionality_score = min(executor.results["score"], 15)  # Cap at 15 pts
                self.final_results["phase_scores"]["functionality"] = functionality_score
                
                print(f"\n✓ Phase 2 Complete")
                print(f"  Functionality: {functionality_score} pts")
                print(f"  Tests Passed: {executor.results['passed']}/{executor.results['total_tests']}")
                
            except Exception as e:
                print(f"\n✗ Phase 2 Failed: {e}")
                self.final_results["summary"].append(f"Functional testing error: {e}")
        else:
            print("\n✗ Could not find database for testing")
            self.final_results["summary"].append("Database not accessible for testing")
        
        # Calculate Final Score
        self.calculate_final_score()
        
        # Generate Report
        self.generate_final_report()
        
        return self.work_dir / "FINAL_GRADE.json"
    def find_extracted_database(self):
        """Find the extracted database directory"""
        # Check Windows temp directory first
        if sys.platform == "win32":
            temp_base = Path(tempfile.gettempdir())
            possible_paths = [
                temp_base / "auto_grading" / "database",
                temp_base / "ultimate_grading" / "database",
                self.work_dir / "database"
            ]
        else:
            possible_paths = [
                Path("/tmp/auto_grading/database"),
                Path("/tmp/ultimate_grading/database"),
                self.work_dir / "database"
            ]
        
        for path in possible_paths:
            if path.exists():
                # Find actual Derby database
                for root, dirs, files in os.walk(path):
                    if 'service.properties' in files or 'log' in dirs:
                        return Path(root)
        
        return None
    
    def clear_database(self, database_dir):
        """Clear all data from database tables"""
        print("\nClearing database for testing...")
        
        try:
            derby_jar = self.find_derby_jar()
            conn = jaydebeapi.connect(
                "org.apache.derby.iapi.jdbc.AutoloadedDriver",
                f"jdbc:derby:{database_dir}",
                ["java", "java"],)
            cursor = conn.cursor()
            
            # Delete in correct order (foreign keys)
            tables = ['SCHEDULE', 'CLASSES', 'STUDENTS', 'COURSES', 'SEMESTER']
            for table in tables:
                try:
                    cursor.execute(f"DELETE FROM {table}")
                    conn.commit()
                    print(f"  ✓ Cleared {table}")
                except:
                    pass
            
            conn.close()
            print("✓ Database cleared")
            
        except Exception as e:
            print(f"⚠ Could not clear database: {e}")
    
    def find_derby_jar(self):
        """Find Derby JAR - Windows compatible"""
        # Common Windows locations
        if sys.platform == "win32":
            common_locations = [
                 r"C:\Users\hetsh\Desktop\db-derby-10.17.1.0-bin\lib\derby.jar",
                r"C:\Derby\lib\derby.jar",
                r"C:\Program Files\Derby\lib\derby.jar",
                r"C:\Apache\Derby\lib\derby.jar",
            ]
            
            # Check Java installation directories
            java_homes = [
                os.environ.get("JAVA_HOME"),
                r"C:\Program Files\Java",
                r"C:\Program Files (x86)\Java"
            ]
            
            for java_home in java_homes:
                if java_home and os.path.exists(java_home):
                    # Search for derby.jar
                    for root, dirs, files in os.walk(java_home):
                        if "derby.jar" in files:
                            common_locations.append(os.path.join(root, "derby.jar"))
        else:
            # Unix locations
            common_locations = [
                "/usr/share/java/derby.jar",
                "/usr/local/derby/lib/derby.jar"
            ]
        
        for loc in common_locations:
            if os.path.exists(loc):
                return loc
        
        # If not found, print helpful message
        print("\n⚠ Warning: Derby JAR not found!")
        print("Download from: https://db.apache.org/derby/derby_downloads.html")
        print("Extract to: C:\\Derby")
        
        return None
    
    def calculate_final_score(self):
        """Calculate final score and grade"""
        total = sum(self.final_results["phase_scores"].values())
        self.final_results["total_score"] = total
        
        # Calculate letter grade
        if total >= 93:
            grade = "A"
        elif total >= 90:
            grade = "A-"
        elif total >= 87:
            grade = "B+"
        elif total >= 83:
            grade = "B"
        elif total >= 80:
            grade = "B-"
        elif total >= 77:
            grade = "C+"
        elif total >= 70:
            grade = "C"
        elif total >= 60:
            grade = "D"
        else:
            grade = "F"
        
        self.final_results["grade_letter"] = grade
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "="*80)
        print(" "*30 + "FINAL GRADE REPORT")
        print("="*80)
        
        print(f"\n📋 Student: {self.final_results['student_name']}")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📦 Part: {self.project_part}")
        
        print("\n" + "-"*80)
        print("SCORE BREAKDOWN")
        print("-"*80)
        
        scores = self.final_results["phase_scores"]
        print(f"Database Structure & Connectivity    {scores['database']:>3} / 55")
        print(f"Code Quality & Design                {scores['code_analysis']:>3} / 20")
        print(f"Compilation & Execution              {scores['compilation']:>3} / 10")
        print(f"Functionality (Test Scripts)         {scores['functionality']:>3} / 15")
        print("-"*80)
        print(f"TOTAL SCORE                          {self.final_results['total_score']:>3} / 100")
        
        print("\n" + "="*80)
        print(f"FINAL GRADE: {self.final_results['grade_letter']}")
        print("="*80)
        
        # Performance summary
        percentage = self.final_results['total_score']
        
        if percentage >= 90:
            emoji = "🎉"
            message = "EXCELLENT - All requirements met!"
        elif percentage >= 80:
            emoji = "👍"
            message = "GOOD - Most requirements met"
        elif percentage >= 70:
            emoji = "⚠️"
            message = "SATISFACTORY - Some issues found"
        else:
            emoji = "❌"
            message = "NEEDS IMPROVEMENT - Major issues found"
        
        print(f"\n{emoji} {message}")
        
        if self.final_results["summary"]:
            print("\n📌 Notes:")
            for note in self.final_results["summary"]:
                print(f"  • {note}")
        
        print("\n" + "="*80)
        print("✓ AUTOMATED GRADING COMPLETE - NO HUMAN REVIEW NEEDED")
        print("="*80)
        
        # Save JSON report
        report_file = self.work_dir / "FINAL_GRADE.json"
        with open(report_file, 'w') as f:
            json.dump(self.final_results, f, indent=2)
        
        # Save human-readable report
        text_report = self.work_dir / "FINAL_GRADE.txt"
        with open(text_report, 'w') as f:
            f.write("="*80 + "\n")
            f.write(" "*30 + "FINAL GRADE REPORT\n")
            f.write("="*80 + "\n\n")
            f.write(f"Student: {self.final_results['student_name']}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Part: {self.project_part}\n\n")
            f.write("-"*80 + "\n")
            f.write("SCORE BREAKDOWN\n")
            f.write("-"*80 + "\n")
            f.write(f"Database Structure & Connectivity    {scores['database']:>3} / 55\n")
            f.write(f"Code Quality & Design                {scores['code_analysis']:>3} / 20\n")
            f.write(f"Compilation & Execution              {scores['compilation']:>3} / 10\n")
            f.write(f"Functionality (Test Scripts)         {scores['functionality']:>3} / 15\n")
            f.write("-"*80 + "\n")
            f.write(f"TOTAL SCORE                          {self.final_results['total_score']:>3} / 100\n\n")
            f.write("="*80 + "\n")
            f.write(f"FINAL GRADE: {self.final_results['grade_letter']}\n")
            f.write("="*80 + "\n")
        
        print(f"\n📄 Text report: {text_report}")
        print(f"📊 JSON report: {report_file}")
        
        return report_file

def main():
    if len(sys.argv) < 3:
        print("="*80)
        print("ULTIMATE 100% AUTOMATED GRADER")
        print("="*80)
        print("\nUsage: python ultimate_autograder.py <project.zip> <database.zip> [part]")
        print("\nThis grader performs:")
        print("  ✓ Database validation")
        print("  ✓ Code analysis")
        print("  ✓ Compilation testing")
        print("  ✓ Functional testing (official test scripts)")
        print("  ✓ Automatic scoring")
        print("\nResult: Complete grade with ZERO human intervention!")
        sys.exit(1)
    
    project_zip = sys.argv[1]
    database_zip = sys.argv[2]
    part = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    
    print(f"\n🚀 Starting ultimate automated grading...")
    print(f"📦 Project: {project_zip}")
    print(f"🗄️  Database: {database_zip}")
    print(f"📋 Part: {part}")
    
    grader = UltimateAutomatedGrader(project_zip, database_zip, part)
    
    try:
        report_file = grader.grade_everything()
        
        if report_file and report_file.exists():
            print(f"\n✅ SUCCESS! Final grade: {grader.final_results['grade_letter']}")
            print(f"📊 Score: {grader.final_results['total_score']}/100")
            return 0
        else:
            print("\n❌ Grading failed")
            return 1
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())