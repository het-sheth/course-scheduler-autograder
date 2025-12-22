#!/usr/bin/env python3
"""Fix grader to accept both singular and plural table names"""

filename = 'fully_automated_grader.py'

with open(filename, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the required_tables definition
old_code = "required_tables = ['SEMESTER', 'COURSES', 'CLASSES', 'STUDENTS', 'SCHEDULE']"

new_code = """required_tables = ['SEMESTER', 'COURSES', 'CLASSES', 'STUDENTS', 'SCHEDULE']
            
            # Also accept singular versions
            singular_map = {
                'COURSES': 'COURSE',
                'CLASSES': 'CLASS',
                'STUDENTS': 'STUDENT'
            }"""

content = content.replace(old_code, new_code)

# Fix the missing tables check
old_check = """missing_tables = [t for t in required_tables if t not in existing_tables]
            
            if not missing_tables:"""

new_check = """# Check for both plural and singular versions
            missing_tables = []
            for table in required_tables:
                if table not in existing_tables:
                    # Check if singular version exists
                    if table in singular_map and singular_map[table] not in existing_tables:
                        missing_tables.append(table)
            
            if not missing_tables:"""

content = content.replace(old_check, new_check)

# Fix the table structures validation to also check singular
old_validate = """expected = {
            'SEMESTER': ['SEMESTERTERM', 'SEMESTERYEAR'],
            'COURSES': ['COURSECODE', 'DESCRIPTION'],
            'CLASSES': ['SEMESTER', 'COURSECODE', 'SEATS'],
            'STUDENTS': ['STUDENTID', 'FIRSTNAME', 'LASTNAME'],
            'SCHEDULE': ['SEMESTER', 'COURSECODE', 'STUDENTID', 'STATUS', 'TIMESTAMP']
        }"""

new_validate = """expected = {
            'SEMESTER': ['SEMESTERTERM', 'SEMESTERYEAR'],
            'COURSES': ['COURSECODE', 'DESCRIPTION'],
            'COURSE': ['COURSECODE', 'DESCRIPTION'],  # Singular
            'CLASSES': ['SEMESTER', 'COURSECODE', 'SEATS'],
            'CLASS': ['SEMESTER', 'COURSECODE', 'SEATS'],  # Singular
            'STUDENTS': ['STUDENTID', 'FIRSTNAME', 'LASTNAME'],
            'STUDENT': ['STUDENTID', 'FIRSTNAME', 'LASTNAME'],  # Singular
            'SCHEDULE': ['SEMESTER', 'COURSECODE', 'STUDENTID', 'STATUS', 'TIMESTAMP']
        }"""

content = content.replace(old_validate, new_validate)

# Fix the empty tables check
old_empty = """for table in required_tables:
                if table in existing_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")"""

new_empty = """for table in required_tables:
                # Check plural first, then singular
                table_to_check = table if table in existing_tables else singular_map.get(table, table)
                if table_to_check in existing_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_to_check}")"""

content = content.replace(old_empty, new_empty)

with open(filename, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed fully_automated_grader.py to accept both singular and plural table names")
print("\nThe grader will now accept:")
print("  - COURSE or COURSES")
print("  - CLASS or CLASSES")
print("  - STUDENT or STUDENTS")