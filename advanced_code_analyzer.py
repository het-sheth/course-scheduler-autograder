#!/usr/bin/env python3
"""
Advanced Code Analyzer for Course Scheduler
Performs deep static analysis of Java code to verify implementations
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
import javalang

class CodeAnalyzer:
    def __init__(self, src_dir: Path):
        self.src_dir = src_dir
        self.java_files = list(src_dir.rglob("*.java"))
        self.analysis_results = {
            "gui_components": {},
            "database_operations": {},
            "classes_found": [],
            "methods_found": {},
            "issues": [],
            "points": 0
        }
    
    def analyze_all(self):
        """Run all analyses"""
        print("\n=== Advanced Code Analysis ===")
        
        for java_file in self.java_files:
            print(f"Analyzing {java_file.name}...")
            content = java_file.read_text(errors='ignore')
            
            # Parse with javalang for AST analysis
            try:
                tree = javalang.parse.parse(content)
                self.analyze_ast(tree, java_file.name)
            except:
                # Fallback to regex-based analysis
                self.analyze_regex(content, java_file.name)
        
        # Specific rubric checks
        self.check_assignment4_requirements()
        self.check_final_project_requirements()
        
        return self.analysis_results
    
    def analyze_ast(self, tree, filename):
        """Analyze using Abstract Syntax Tree"""
        for path, node in tree:
            # Find class declarations
            if isinstance(node, javalang.tree.ClassDeclaration):
                self.analysis_results["classes_found"].append(node.name)
            
            # Find field declarations (GUI components)
            if isinstance(node, javalang.tree.FieldDeclaration):
                for declarator in node.declarators:
                    component_type = node.type.name
                    component_name = declarator.name
                    
                    if component_type in ['JFrame', 'JButton', 'JLabel', 'JTextField', 
                                         'JComboBox', 'JPanel', 'JCheckBox', 'JSpinner']:
                        if filename not in self.analysis_results["gui_components"]:
                            self.analysis_results["gui_components"][filename] = []
                        
                        self.analysis_results["gui_components"][filename].append({
                            "type": component_type,
                            "name": component_name
                        })
            
            # Find method declarations
            if isinstance(node, javalang.tree.MethodDeclaration):
                if filename not in self.analysis_results["methods_found"]:
                    self.analysis_results["methods_found"][filename] = []
                
                self.analysis_results["methods_found"][filename].append({
                    "name": node.name,
                    "return_type": node.return_type,
                    "parameters": len(node.parameters) if node.parameters else 0
                })
    
    def analyze_regex(self, content: str, filename: str):
        """Fallback regex-based analysis"""
        
        # Find GUI components
        gui_patterns = {
            'JFrame': r'JFrame\s+(\w+)',
            'JButton': r'JButton\s+(\w+)',
            'JLabel': r'JLabel\s+(\w+)',
            'JTextField': r'JTextField\s+(\w+)',
            'JComboBox': r'JComboBox<?[^>]*>?\s+(\w+)',
            'JPanel': r'JPanel\s+(\w+)',
            'JCheckBox': r'JCheckBox\s+(\w+)',
            'JSpinner': r'JSpinner\s+(\w+)'
        }
        
        for comp_type, pattern in gui_patterns.items():
            matches = re.findall(pattern, content)
            for match in matches:
                if filename not in self.analysis_results["gui_components"]:
                    self.analysis_results["gui_components"][filename] = []
                
                self.analysis_results["gui_components"][filename].append({
                    "type": comp_type,
                    "name": match
                })
        
        # Find database operations
        db_patterns = {
            'PreparedStatement': r'PreparedStatement\s+(\w+)',
            'executeUpdate': r'\.executeUpdate\(',
            'executeQuery': r'\.executeQuery\(',
            'SQL_Injection_Risk': r'executeUpdate\([^)]*\+|executeQuery\([^)]*\+'
        }
        
        for op_type, pattern in db_patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                if filename not in self.analysis_results["database_operations"]:
                    self.analysis_results["database_operations"][filename] = []
                
                self.analysis_results["database_operations"][filename].append({
                    "operation": op_type,
                    "count": len(matches)
                })
    
    def check_assignment4_requirements(self):
        """Check Assignment 4 (Fahrenheit to Celsius) specific requirements"""
        print("\nChecking Assignment 4 requirements...")
        
        requirements = {
            "JFrame with title": False,
            "Title JLabel (red)": False,
            "Fahrenheit JTextField": False,
            "Convert JButton": False,
            "Celsius JLabel": False,
            "ActionListener": False,
            "BorderLayout": False
        }
        
        all_content = ""
        for java_file in self.java_files:
            all_content += java_file.read_text(errors='ignore')
        
        # Check for JFrame title
        if re.search(r'setTitle\s*\(\s*["\'].*Temperature.*Converter.*["\']', all_content):
            requirements["JFrame with title"] = True
            self.analysis_results["points"] += 5
        
        # Check for red colored label
        if re.search(r'setForeground\s*\(\s*Color\.RED', all_content, re.IGNORECASE):
            requirements["Title JLabel (red)"] = True
            self.analysis_results["points"] += 5
        
        # Check for JTextField
        if 'JTextField' in all_content:
            requirements["Fahrenheit JTextField"] = True
            self.analysis_results["points"] += 5
        
        # Check for JButton with "Convert"
        if re.search(r'JButton.*["\']Convert["\']|setText\s*\(\s*["\']Convert["\']', all_content):
            requirements["Convert JButton"] = True
            self.analysis_results["points"] += 5
        
        # Check for ActionListener implementation
        if 'ActionListener' in all_content or 'actionPerformed' in all_content:
            requirements["ActionListener"] = True
            self.analysis_results["points"] += 5
        
        # Check for BorderLayout
        if 'BorderLayout' in all_content:
            requirements["BorderLayout"] = True
            self.analysis_results["points"] += 5
        
        # Check for Celsius label
        if re.search(r'Celsius|celsius', all_content):
            requirements["Celsius JLabel"] = True
            self.analysis_results["points"] += 5
        
        # Report findings
        for req, found in requirements.items():
            if found:
                print(f"  ✓ {req}")
            else:
                print(f"  ✗ {req}")
                self.analysis_results["issues"].append(f"Missing: {req}")
    
    def check_final_project_requirements(self):
        """Check Final Project specific requirements"""
        print("\nChecking Final Project requirements...")
        
        required_classes = {
            "SemesterEntry": False,
            "CourseEntry": False,
            "ClassEntry": False,
            "StudentEntry": False,
            "ScheduleEntry": False,
            "SemesterQueries": False,
            "CourseQueries": False,
            "ClassQueries": False,
            "StudentQueries": False,
            "ScheduleQueries": False
        }
        
        found_classes = self.analysis_results["classes_found"]
        
        for req_class in required_classes.keys():
            if req_class in found_classes:
                required_classes[req_class] = True
                self.analysis_results["points"] += 5
                print(f"  ✓ Found class: {req_class}")
            else:
                print(f"  ✗ Missing class: {req_class}")
                self.analysis_results["issues"].append(f"Missing class: {req_class}")
        
        # Check for JComboBox usage
        combo_box_count = 0
        for components in self.analysis_results["gui_components"].values():
            combo_box_count += sum(1 for c in components if c["type"] == "JComboBox")
        
        if combo_box_count >= 3:
            print(f"  ✓ Found {combo_box_count} JComboBox components")
            self.analysis_results["points"] += 5
        else:
            print(f"  ✗ Only found {combo_box_count} JComboBox (need at least 3)")
            self.analysis_results["issues"].append("Not enough JComboBox components")
    
    def check_sql_security(self):
        """Check for SQL injection vulnerabilities"""
        print("\nChecking SQL security...")
        
        has_prepared_statements = False
        has_sql_injection_risk = False
        
        for filename, operations in self.analysis_results["database_operations"].items():
            for op in operations:
                if op["operation"] == "PreparedStatement":
                    has_prepared_statements = True
                if op["operation"] == "SQL_Injection_Risk":
                    has_sql_injection_risk = True
                    print(f"  ⚠ SQL Injection risk in {filename}")
                    self.analysis_results["issues"].append(f"SQL Injection risk in {filename}")
        
        if has_prepared_statements:
            print("  ✓ Uses PreparedStatements")
            self.analysis_results["points"] += 10
        else:
            print("  ✗ Does not use PreparedStatements")
            self.analysis_results["issues"].append("Does not use PreparedStatements")
        
        if has_sql_injection_risk:
            self.analysis_results["points"] -= 5
    
    def generate_report(self):
        """Generate detailed analysis report"""
        print("\n" + "="*60)
        print("CODE ANALYSIS REPORT")
        print("="*60)
        
        print(f"\nFiles analyzed: {len(self.java_files)}")
        print(f"Classes found: {len(self.analysis_results['classes_found'])}")
        
        print(f"\nGUI Components:")
        for filename, components in self.analysis_results["gui_components"].items():
            print(f"  {filename}:")
            comp_counts = {}
            for comp in components:
                comp_type = comp["type"]
                comp_counts[comp_type] = comp_counts.get(comp_type, 0) + 1
            
            for comp_type, count in comp_counts.items():
                print(f"    {comp_type}: {count}")
        
        print(f"\nIssues Found: {len(self.analysis_results['issues'])}")
        for issue in self.analysis_results["issues"]:
            print(f"  - {issue}")
        
        print(f"\nEstimated Points (from code analysis): {self.analysis_results['points']}")
        print("="*60)
        
        return self.analysis_results


class FunctionalityTester:
    """
    Tests actual functionality by compiling and running code
    """
    
    def __init__(self, project_dir: Path, database_dir: Path):
        self.project_dir = project_dir
        self.database_dir = database_dir
        self.test_results = {
            "compilation": False,
            "database_connection": False,
            "gui_launches": False,
            "add_operations": {},
            "display_operations": {},
            "points": 0
        }
    
    def compile_project(self):
        """Compile the Java project"""
        print("\n=== Compiling Project ===")
        
        import subprocess
        
        # Find source files
        src_dir = self.project_dir / "src"
        if not src_dir.exists():
            print("✗ Source directory not found")
            return False
        
        java_files = list(src_dir.rglob("*.java"))
        if not java_files:
            print("✗ No Java files found")
            return False
        
        # Create build directory
        build_dir = self.project_dir / "build"
        build_dir.mkdir(exist_ok=True)
        
        # Compile
        try:
            classpath = self.get_classpath()
            
            cmd = [
                "javac",
                "-d", str(build_dir),
                "-cp", classpath,
                *[str(f) for f in java_files]
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✓ Compilation successful")
                self.test_results["compilation"] = True
                self.test_results["points"] += 10
                return True
            else:
                print(f"✗ Compilation failed:\n{result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Compilation error: {e}")
            return False
    
    def get_classpath(self):
        """Build classpath including Derby and other dependencies"""
        classpath_parts = [
            str(self.project_dir / "build"),
            "/usr/share/java/derby.jar",
            "/usr/share/java/derbytools.jar"
        ]
        
        return ":".join(classpath_parts)
    
    def test_database_connection(self):
        """Test if code can connect to database"""
        print("\n=== Testing Database Connection ===")
        
        # This would run the student's code and check if it can connect
        # For now, we check if database access code exists
        
        src_dir = self.project_dir / "src"
        found_connection_code = False
        
        for java_file in src_dir.rglob("*.java"):
            content = java_file.read_text(errors='ignore')
            if 'DriverManager.getConnection' in content or 'jdbc:derby' in content:
                found_connection_code = True
                print("✓ Database connection code found")
                self.test_results["points"] += 5
                break
        
        if not found_connection_code:
            print("✗ No database connection code found")
        
        return found_connection_code
    
    def test_gui_components_programmatically(self):
        """Test GUI components using reflection and introspection"""
        print("\n=== Testing GUI Components ===")
        
        # We can use jython or Py4J to interact with Java classes
        # For now, we do static analysis
        
        src_dir = self.project_dir / "src"
        
        for java_file in src_dir.rglob("*.java"):
            content = java_file.read_text(errors='ignore')
            
            # Check for proper component initialization
            checks = {
                "JFrame size set": r'setSize\s*\(',
                "JFrame visible": r'setVisible\s*\(\s*true',
                "Event listeners added": r'addActionListener\s*\(',
                "Layout manager": r'setLayout\s*\(',
                "Components added": r'add\s*\('
            }
            
            for check_name, pattern in checks.items():
                if re.search(pattern, content):
                    print(f"  ✓ {check_name}")
                    self.test_results["points"] += 2
                else:
                    print(f"  ✗ {check_name}")
    
    def run_tests(self):
        """Run all functional tests"""
        self.compile_project()
        self.test_database_connection()
        self.test_gui_components_programmatically()
        
        return self.test_results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python advanced_code_analyzer.py <project_src_dir>")
        sys.exit(1)
    
    src_dir = Path(sys.argv[1])
    
    analyzer = CodeAnalyzer(src_dir)
    results = analyzer.analyze_all()
    analyzer.check_sql_security()
    analyzer.generate_report()
