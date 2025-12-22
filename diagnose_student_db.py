#!/usr/bin/env python3
"""Diagnose student database"""

import os
import sys
import jpype
import jaydebeapi
import zipfile
import tempfile
from pathlib import Path

# Initialize JVM
if not jpype.isJVMStarted():
    os.environ['JAVA_HOME'] = r'C:\Program Files\Java\jdk-21'
    jvm_path = os.path.join(os.environ['JAVA_HOME'], 'bin', 'server', 'jvm.dll')
    jpype.startJVM(jvm_path, convertStrings=False)
    jpype.addClassPath(r"C:\Derby\lib\derby.jar")

print("=" * 70)
print("STUDENT DATABASE DIAGNOSTIC")
print("=" * 70)

# Extract database
db_zip = "CourseSchedulerDBkumarduvvapukbd5562PART2.zip"
temp_dir = Path(tempfile.gettempdir()) / "student_db_diag"
temp_dir.mkdir(exist_ok=True)

with zipfile.ZipFile(db_zip, 'r') as zip_ref:
    zip_ref.extractall(temp_dir)

# Find database
print(f"\n1. Database contents:")
for root, dirs, files in os.walk(temp_dir):
    level = root.replace(str(temp_dir), '').count(os.sep)
    indent = ' ' * 2 * level
    print(f'{indent}{os.path.basename(root)}/')
    subindent = ' ' * 2 * (level + 1)
    for file in files[:10]:  # First 10 files
        print(f'{subindent}{file}')

# Find Derby database root
db_root = None
for root, dirs, files in os.walk(temp_dir):
    if 'service.properties' in files or 'log' in dirs:
        db_root = Path(root)
        break

if not db_root:
    print("\n✗ Could not find Derby database!")
    sys.exit(1)

print(f"\n2. Database root: {db_root}")

# Connect and check tables
try:
    conn = jaydebeapi.connect(
        "org.apache.derby.iapi.jdbc.AutoloadedDriver",
        f"jdbc:derby:{db_root}",
        ["java", "java"]
    )
    
    cursor = conn.cursor()
    
    # Get all tables
    print(f"\n3. All tables in database:")
    cursor.execute("SELECT TABLENAME, TABLETYPE FROM SYS.SYSTABLES WHERE TABLETYPE='T' ORDER BY TABLENAME")
    tables = cursor.fetchall()
    
    if tables:
        for table_name, table_type in tables:
            print(f"   - {table_name} ({table_type})")
            
            # Get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"     Rows: {count}")
            except:
                pass
            
            # Get columns
            try:
                cursor.execute(f"SELECT * FROM {table_name} WHERE 1=0")
                cols = [desc[0] for desc in cursor.description]
                print(f"     Columns: {', '.join(cols)}")
            except:
                pass
    else:
        print("   ✗ No tables found!")
    
    conn.close()
    
    print(f"\n" + "=" * 70)
    print("DIAGNOSIS COMPLETE")
    print("=" * 70)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()