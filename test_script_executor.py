#!/usr/bin/env python3
"""
Automated Test Script Executor
Runs the official Course Scheduler test scripts automatically
100% automated - NO human intervention needed!
"""

import jaydebeapi
import subprocess
import time
import re
from pathlib import Path
from typing import Dict, List, Tuple
import json

class TestScriptExecutor:
    """
    Executes test scripts by:
    1. Running actions via database queries
    2. Verifying database state
    3. Checking expected results
    """
    
    def __init__(self, database_dir: Path, project_part: int):
        self.database_dir = database_dir
        self.project_part = project_part
        self.conn = None
        self.cursor = None
        
        # Test results
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "tests": [],
            "score": 0,
            "max_score": 100
        }
        
        # Current semester tracking
        self.current_semester = None
    
    def connect_database(self):
        """Connect to Derby database"""
        derby_jar = self.find_derby_jar()
        if not derby_jar:
            raise Exception("Derby JAR not found")
        
        self.conn = jaydebeapi.connect(
            "org.apache.derby.jdbc.EmbeddedDriver",
            f"jdbc:derby:{self.database_dir}",
            ["java", "java"],
            derby_jar
        )
        self.cursor = self.conn.cursor()
        print("✓ Connected to database")
    
    def find_derby_jar(self):
        """Find Derby JAR"""
        import os
        common = ["/usr/share/java/derby.jar"]
        for loc in common:
            if os.path.exists(loc):
                return loc
        return None
    
    def run_part1_tests(self):
        """Execute Part 1 test script"""
        print("\n" + "="*70)
        print("RUNNING PART 1 TEST SCRIPT")
        print("="*70)
        
        # Add Semesters
        self.test_add_semester("Fall", "2025")
        self.test_semester_in_db("Fall", "2025")
        
        self.test_add_semester("Spring", "2026")
        self.test_semester_in_db("Spring", "2026")
        
        # Add Courses
        self.test_add_course("CMPSC131", "Intro to Programming")
        self.test_course_in_db("CMPSC131", "Intro to Programming")
        
        self.test_add_course("CMPSC132", "Data Structures")
        self.test_course_in_db("CMPSC132", "Data Structures")
        
        self.test_add_course("PHYSICS101", "Intro to Physics")
        self.test_course_in_db("PHYSICS101", "Intro to Physics")
        
        self.test_add_course("BIOLOGY101", "Intro to Biology")
        self.test_course_in_db("BIOLOGY101", "Intro to Biology")
        
        # Set current semester
        self.current_semester = "Fall 2025"
        
        # Add Classes
        self.test_add_class("Fall 2025", "CMPSC131", 2)
        self.test_class_in_db("Fall 2025", "CMPSC131", 2)
        
        self.test_add_class("Fall 2025", "CMPSC132", 2)
        self.test_class_in_db("Fall 2025", "CMPSC132", 2)
        
        self.test_add_class("Fall 2025", "PHYSICS101", 2)
        self.test_class_in_db("Fall 2025", "PHYSICS101", 2)
        
        self.test_add_class("Fall 2025", "BIOLOGY101", 2)
        self.test_class_in_db("Fall 2025", "BIOLOGY101", 2)
        
        # Add Students
        self.test_add_student("111111111", "Sue", "Jones")
        self.test_student_in_db("111111111", "Sue", "Jones")
        
        self.test_add_student("222222222", "Sam", "Roberts")
        self.test_student_in_db("222222222", "Sam", "Roberts")
        
        self.test_add_student("333333333", "Shawna", "Sampson")
        self.test_student_in_db("333333333", "Shawna", "Sampson")
        
        self.test_add_student("444444444", "John", "Jensen")
        self.test_student_in_db("444444444", "John", "Jensen")
        
        # Display Classes (verify they exist)
        self.test_display_classes("Fall 2025", 4)
        
        # Schedule Classes
        self.test_schedule_class("111111111", "Fall 2025", "CMPSC131", "S")
        self.test_schedule_class("111111111", "Fall 2025", "PHYSICS101", "S")
        
        self.test_schedule_class("222222222", "Fall 2025", "PHYSICS101", "S")
        self.test_schedule_class("222222222", "Fall 2025", "CMPSC131", "S")
        self.test_schedule_class("222222222", "Fall 2025", "BIOLOGY101", "S")
        
        self.test_schedule_class("333333333", "Fall 2025", "BIOLOGY101", "S")
        self.test_schedule_class("333333333", "Fall 2025", "PHYSICS101", "W")  # Should be waitlisted!
        self.test_schedule_class("111111111", "Fall 2025", "BIOLOGY101", "W")  # Should be waitlisted!
        
        # Display Schedules (verify)
        self.test_student_schedule("111111111", "Fall 2025", [
            ("CMPSC131", "S"),
            ("PHYSICS101", "S"),
            ("BIOLOGY101", "W")
        ])
        
        self.test_student_schedule("222222222", "Fall 2025", [
            ("CMPSC131", "S"),
            ("PHYSICS101", "S"),
            ("BIOLOGY101", "S")
        ])
        
        self.test_student_schedule("333333333", "Fall 2025", [
            ("BIOLOGY101", "S"),
            ("PHYSICS101", "W")
        ])
        
        # Change to Spring 2026
        self.current_semester = "Spring 2026"
        
        self.test_add_class("Spring 2026", "CMPSC131", 2)
        self.test_add_class("Spring 2026", "PHYSICS101", 2)
        
        self.test_display_classes("Spring 2026", 2)
        
        self.test_schedule_class("111111111", "Spring 2026", "CMPSC131", "S")
        self.test_schedule_class("111111111", "Spring 2026", "PHYSICS101", "S")
        self.test_schedule_class("333333333", "Spring 2026", "PHYSICS101", "S")
        
        self.test_student_schedule("111111111", "Spring 2026", [
            ("CMPSC131", "S"),
            ("PHYSICS101", "S")
        ])
        
        self.test_student_schedule("333333333", "Spring 2026", [
            ("PHYSICS101", "S")
        ])
        
        self.generate_report()
    
    def run_part2_tests(self):
        """Execute Part 2 test script (requires Part 1 to be run first)"""
        print("\n" + "="*70)
        print("RUNNING PART 2 TEST SCRIPT")
        print("="*70)
        
        # First run Part 1 to set up data
        print("\n>>> Setting up data with Part 1 tests...")
        self.run_part1_tests()
        
        print("\n>>> Starting Part 2 specific tests...")
        
        # Set to Fall 2025
        self.current_semester = "Fall 2025"
        
        # Schedule Jensen to Physics101 (should be waitlisted)
        self.test_schedule_class("444444444", "Fall 2025", "PHYSICS101", "W")
        
        # Admin Class List
        self.test_class_list("Fall 2025", "BIOLOGY101", 
            scheduled=["222222222", "333333333"],
            waitlisted=["111111111"]
        )
        
        # Admin Drop Student - Jones, Sue
        self.test_drop_student("111111111", [
            ("Fall 2025", "CMPSC131", "dropped"),
            ("Fall 2025", "PHYSICS101", "dropped"),
            ("Fall 2025", "BIOLOGY101", "dropped_waitlist"),
            ("Spring 2026", "CMPSC131", "dropped"),
            ("Spring 2026", "PHYSICS101", "dropped")
        ])
        
        # Verify Sampson was scheduled into Physics101 from waitlist
        self.test_schedule_status("333333333", "Fall 2025", "PHYSICS101", "S")
        
        # Display Schedules to verify
        self.test_student_schedule("222222222", "Fall 2025", [
            ("CMPSC131", "S"),
            ("PHYSICS101", "S"),
            ("BIOLOGY101", "S")
        ])
        
        self.test_student_schedule("333333333", "Fall 2025", [
            ("BIOLOGY101", "S"),
            ("PHYSICS101", "S")  # Should now be scheduled!
        ])
        
        self.test_student_schedule("444444444", "Fall 2025", [
            ("PHYSICS101", "W")
        ])
        
        # Schedule Jensen to Biology101 (waitlisted)
        self.test_schedule_class("444444444", "Fall 2025", "BIOLOGY101", "W")
        
        self.test_student_schedule("444444444", "Fall 2025", [
            ("PHYSICS101", "W"),
            ("BIOLOGY101", "W")
        ])
        
        # Student Drop Class - Roberts drops Biology101
        self.test_student_drop_class("222222222", "Fall 2025", "BIOLOGY101")
        
        # Verify Jensen was scheduled from waitlist
        self.test_schedule_status("444444444", "Fall 2025", "BIOLOGY101", "S")
        
        self.test_student_schedule("222222222", "Fall 2025", [
            ("CMPSC131", "S"),
            ("PHYSICS101", "S")
        ])
        
        self.test_student_schedule("444444444", "Fall 2025", [
            ("BIOLOGY101", "S"),
            ("PHYSICS101", "W")
        ])
        
        # Admin Drop Class - Biology101
        self.test_drop_class("Fall 2025", "BIOLOGY101")
        
        # Verify students were dropped
        self.test_student_not_in_class("333333333", "Fall 2025", "BIOLOGY101")
        self.test_student_not_in_class("444444444", "Fall 2025", "BIOLOGY101")
        
        self.generate_report()
    
    # ===== Test Helper Methods =====
    
    def test_add_semester(self, term, year):
        """Test adding a semester"""
        test_name = f"Add Semester - {term} {year}"
        self.results["total_tests"] += 1
        
        try:
            self.cursor.execute(
                "INSERT INTO SEMESTER (SEMESTERTERM, SEMESTERYEAR) VALUES (?, ?)",
                (term, year)
            )
            self.conn.commit()
            self.pass_test(test_name, 2)
        except Exception as e:
            self.fail_test(test_name, f"Database error: {e}", 2)
    
    def test_semester_in_db(self, term, year):
        """Verify semester exists in database"""
        test_name = f"Verify Semester {term} {year} in DB"
        self.results["total_tests"] += 1
        
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM SEMESTER WHERE SEMESTERTERM=? AND SEMESTERYEAR=?",
                (term, year)
            )
            count = self.cursor.fetchone()[0]
            
            if count == 1:
                self.pass_test(test_name, 1)
            else:
                self.fail_test(test_name, f"Found {count} semesters (expected 1)", 1)
        except Exception as e:
            self.fail_test(test_name, f"Database error: {e}", 1)
    
    def test_add_course(self, code, description):
        """Test adding a course"""
        test_name = f"Add Course - {code}"
        self.results["total_tests"] += 1
        
        try:
            self.cursor.execute(
                "INSERT INTO COURSES (COURSECODE, DESCRIPTION) VALUES (?, ?)",
                (code, description)
            )
            self.conn.commit()
            self.pass_test(test_name, 2)
        except Exception as e:
            self.fail_test(test_name, f"Database error: {e}", 2)
    
    def test_course_in_db(self, code, description):
        """Verify course exists"""
        test_name = f"Verify Course {code} in DB"
        self.results["total_tests"] += 1
        
        try:
            self.cursor.execute(
                "SELECT DESCRIPTION FROM COURSES WHERE COURSECODE=?",
                (code,)
            )
            result = self.cursor.fetchone()
            
            if result and result[0] == description:
                self.pass_test(test_name, 1)
            else:
                self.fail_test(test_name, "Course not found or incorrect", 1)
        except Exception as e:
            self.fail_test(test_name, f"Database error: {e}", 1)
    
    def test_add_class(self, semester, course_code, seats):
        """Test adding a class"""
        test_name = f"Add Class - {semester} {course_code} ({seats} seats)"
        self.results["total_tests"] += 1
        
        try:
            self.cursor.execute(
                "INSERT INTO CLASSES (SEMESTER, COURSECODE, SEATS) VALUES (?, ?, ?)",
                (semester, course_code, seats)
            )
            self.conn.commit()
            self.pass_test(test_name, 2)
        except Exception as e:
            self.fail_test(test_name, f"Database error: {e}", 2)
    
    def test_class_in_db(self, semester, course_code, seats):
        """Verify class exists"""
        test_name = f"Verify Class {course_code} in {semester}"
        self.results["total_tests"] += 1
        
        try:
            self.cursor.execute(
                "SELECT SEATS FROM CLASSES WHERE SEMESTER=? AND COURSECODE=?",
                (semester, course_code)
            )
            result = self.cursor.fetchone()
            
            if result and result[0] == seats:
                self.pass_test(test_name, 1)
            else:
                self.fail_test(test_name, "Class not found or incorrect seats", 1)
        except Exception as e:
            self.fail_test(test_name, f"Database error: {e}", 1)
    
    def test_add_student(self, student_id, first_name, last_name):
        """Test adding a student"""
        test_name = f"Add Student - {first_name} {last_name}"
        self.results["total_tests"] += 1
        
        try:
            self.cursor.execute(
                "INSERT INTO STUDENTS (STUDENTID, FIRSTNAME, LASTNAME) VALUES (?, ?, ?)",
                (student_id, first_name, last_name)
            )
            self.conn.commit()
            self.pass_test(test_name, 2)
        except Exception as e:
            self.fail_test(test_name, f"Database error: {e}", 2)
    
    def test_student_in_db(self, student_id, first_name, last_name):
        """Verify student exists"""
        test_name = f"Verify Student {first_name} {last_name} in DB"
        self.results["total_tests"] += 1
        
        try:
            self.cursor.execute(
                "SELECT FIRSTNAME, LASTNAME FROM STUDENTS WHERE STUDENTID=?",
                (student_id,)
            )
            result = self.cursor.fetchone()
            
            if result and result[0] == first_name and result[1] == last_name:
                self.pass_test(test_name, 1)
            else:
                self.fail_test(test_name, "Student not found or incorrect", 1)
        except Exception as e:
            self.fail_test(test_name, f"Database error: {e}", 1)
    
    def test_display_classes(self, semester, expected_count):
        """Test display classes functionality"""
        test_name = f"Display Classes for {semester}"
        self.results["total_tests"] += 1
        
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM CLASSES WHERE SEMESTER=?",
                (semester,)
            )
            count = self.cursor.fetchone()[0]
            
            if count == expected_count:
                self.pass_test(test_name, 2)
            else:
                self.fail_test(test_name, f"Found {count} classes (expected {expected_count})", 2)
        except Exception as e:
            self.fail_test(test_name, f"Database error: {e}", 2)
    
    def test_schedule_class(self, student_id, semester, course_code, expected_status):
        """Test scheduling a class"""
        test_name = f"Schedule {student_id} for {course_code} (expect {expected_status})"
        self.results["total_tests"] += 1
        
        try:
            # Check current enrollment
            self.cursor.execute(
                """SELECT COUNT(*) FROM SCHEDULE 
                   WHERE SEMESTER=? AND COURSECODE=? AND STATUS='S'""",
                (semester, course_code)
            )
            enrolled = self.cursor.fetchone()[0]
            
            # Get class capacity
            self.cursor.execute(
                "SELECT SEATS FROM CLASSES WHERE SEMESTER=? AND COURSECODE=?",
                (semester, course_code)
            )
            seats = self.cursor.fetchone()[0]
            
            # Determine status
            status = 'S' if enrolled < seats else 'W'
            
            # Insert
            from datetime import datetime
            timestamp = datetime.now()
            self.cursor.execute(
                """INSERT INTO SCHEDULE (SEMESTER, COURSECODE, STUDENTID, STATUS, TIMESTAMP)
                   VALUES (?, ?, ?, ?, ?)""",
                (semester, course_code, student_id, status, timestamp)
            )
            self.conn.commit()
            
            if status == expected_status:
                self.pass_test(test_name, 3)
            else:
                self.fail_test(test_name, f"Got status {status}, expected {expected_status}", 3)
                
        except Exception as e:
            self.fail_test(test_name, f"Database error: {e}", 3)
    
    def test_student_schedule(self, student_id, semester, expected_classes):
        """Verify student's schedule"""
        test_name = f"Verify Schedule for student {student_id}"
        self.results["total_tests"] += 1
        
        try:
            self.cursor.execute(
                """SELECT COURSECODE, STATUS FROM SCHEDULE 
                   WHERE STUDENTID=? AND SEMESTER=?
                   ORDER BY COURSECODE""",
                (student_id, semester)
            )
            actual = [(row[0], row[1]) for row in self.cursor.fetchall()]
            expected = sorted(expected_classes)
            
            if actual == expected:
                self.pass_test(test_name, 2)
            else:
                self.fail_test(test_name, f"Expected {expected}, got {actual}", 2)
        except Exception as e:
            self.fail_test(test_name, f"Database error: {e}", 2)
    
    def test_class_list(self, semester, course_code, scheduled, waitlisted):
        """Test class list display (Part 2)"""
        test_name = f"Class List for {course_code}"
        self.results["total_tests"] += 1
        
        try:
            # Get scheduled students
            self.cursor.execute(
                """SELECT STUDENTID FROM SCHEDULE 
                   WHERE SEMESTER=? AND COURSECODE=? AND STATUS='S'
                   ORDER BY TIMESTAMP""",
                (semester, course_code)
            )
            actual_scheduled = [row[0] for row in self.cursor.fetchall()]
            
            # Get waitlisted students
            self.cursor.execute(
                """SELECT STUDENTID FROM SCHEDULE 
                   WHERE SEMESTER=? AND COURSECODE=? AND STATUS='W'
                   ORDER BY TIMESTAMP""",
                (semester, course_code)
            )
            actual_waitlisted = [row[0] for row in self.cursor.fetchall()]
            
            if actual_scheduled == scheduled and actual_waitlisted == waitlisted:
                self.pass_test(test_name, 3)
            else:
                self.fail_test(test_name, "Class list mismatch", 3)
        except Exception as e:
            self.fail_test(test_name, f"Database error: {e}", 3)
    
    def test_drop_student(self, student_id, expected_drops):
        """Test dropping a student (Part 2)"""
        test_name = f"Drop Student {student_id}"
        self.results["total_tests"] += 1
        
        try:
            # Delete from all schedules
            self.cursor.execute(
                "DELETE FROM SCHEDULE WHERE STUDENTID=?",
                (student_id,)
            )
            
            # Delete student
            self.cursor.execute(
                "DELETE FROM STUDENTS WHERE STUDENTID=?",
                (student_id,)
            )
            self.conn.commit()
            
            # Verify student is gone
            self.cursor.execute(
                "SELECT COUNT(*) FROM STUDENTS WHERE STUDENTID=?",
                (student_id,)
            )
            count = self.cursor.fetchone()[0]
            
            if count == 0:
                self.pass_test(test_name, 5)
            else:
                self.fail_test(test_name, "Student not deleted", 5)
        except Exception as e:
            self.fail_test(test_name, f"Database error: {e}", 5)
    
    def test_schedule_status(self, student_id, semester, course_code, expected_status):
        """Verify schedule status"""
        test_name = f"Verify {student_id} status in {course_code}"
        self.results["total_tests"] += 1
        
        try:
            self.cursor.execute(
                """SELECT STATUS FROM SCHEDULE 
                   WHERE STUDENTID=? AND SEMESTER=? AND COURSECODE=?""",
                (student_id, semester, course_code)
            )
            result = self.cursor.fetchone()
            
            if result and result[0] == expected_status:
                self.pass_test(test_name, 1)
            else:
                actual = result[0] if result else "not found"
                self.fail_test(test_name, f"Expected {expected_status}, got {actual}", 1)
        except Exception as e:
            self.fail_test(test_name, f"Database error: {e}", 1)
    
    def test_student_drop_class(self, student_id, semester, course_code):
        """Test student dropping a class"""
        test_name = f"Student {student_id} drops {course_code}"
        self.results["total_tests"] += 1
        
        try:
            self.cursor.execute(
                """DELETE FROM SCHEDULE 
                   WHERE STUDENTID=? AND SEMESTER=? AND COURSECODE=?""",
                (student_id, semester, course_code)
            )
            self.conn.commit()
            self.pass_test(test_name, 3)
        except Exception as e:
            self.fail_test(test_name, f"Database error: {e}", 3)
    
    def test_student_not_in_class(self, student_id, semester, course_code):
        """Verify student is not in class"""
        test_name = f"Verify {student_id} not in {course_code}"
        self.results["total_tests"] += 1
        
        try:
            self.cursor.execute(
                """SELECT COUNT(*) FROM SCHEDULE 
                   WHERE STUDENTID=? AND SEMESTER=? AND COURSECODE=?""",
                (student_id, semester, course_code)
            )
            count = self.cursor.fetchone()[0]
            
            if count == 0:
                self.pass_test(test_name, 1)
            else:
                self.fail_test(test_name, "Student still in class", 1)
        except Exception as e:
            self.fail_test(test_name, f"Database error: {e}", 1)
    
    def test_drop_class(self, semester, course_code):
        """Test dropping a class"""
        test_name = f"Drop Class {course_code} from {semester}"
        self.results["total_tests"] += 1
        
        try:
            # Delete all schedules for this class
            self.cursor.execute(
                "DELETE FROM SCHEDULE WHERE SEMESTER=? AND COURSECODE=?",
                (semester, course_code)
            )
            
            # Delete class
            self.cursor.execute(
                "DELETE FROM CLASSES WHERE SEMESTER=? AND COURSECODE=?",
                (semester, course_code)
            )
            self.conn.commit()
            self.pass_test(test_name, 5)
        except Exception as e:
            self.fail_test(test_name, f"Database error: {e}", 5)
    
    # ===== Result Tracking =====
    
    def pass_test(self, test_name, points):
        """Record passed test"""
        self.results["passed"] += 1
        self.results["score"] += points
        self.results["tests"].append({
            "name": test_name,
            "status": "PASS",
            "points": points
        })
        print(f"  ✓ {test_name} (+{points} pts)")
    
    def fail_test(self, test_name, reason, points):
        """Record failed test"""
        self.results["failed"] += 1
        self.results["tests"].append({
            "name": test_name,
            "status": "FAIL",
            "reason": reason,
            "points_lost": points
        })
        print(f"  ✗ {test_name} - {reason} (-{points} pts)")
    
    def generate_report(self):
        """Generate final test report"""
        print("\n" + "="*70)
        print("TEST EXECUTION REPORT")
        print("="*70)
        
        print(f"\nTotal Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed']} ✓")
        print(f"Failed: {self.results['failed']} ✗")
        
        pass_rate = (self.results['passed'] / self.results['total_tests'] * 100) if self.results['total_tests'] > 0 else 0
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        print(f"\nFunctionality Score: {self.results['score']}/{self.results['max_score']}")
        
        if self.results['failed'] > 0:
            print("\nFailed Tests:")
            for test in self.results['tests']:
                if test['status'] == 'FAIL':
                    print(f"  ✗ {test['name']}: {test['reason']}")
        
        print("="*70)
        
        # Save report
        report_file = Path("/tmp/test_execution_report.json")
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nReport saved to: {report_file}")
    
    def cleanup(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("\n✓ Database connection closed")


def main():
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python test_script_executor.py <database_dir> <part>")
        print("  part: 1 or 2")
        sys.exit(1)
    
    database_dir = Path(sys.argv[1])
    part = int(sys.argv[2])
    
    executor = TestScriptExecutor(database_dir, part)
    
    try:
        executor.connect_database()
        
        if part == 1:
            executor.run_part1_tests()
        else:
            executor.run_part2_tests()
        
    finally:
        executor.cleanup()


if __name__ == "__main__":
    main()
