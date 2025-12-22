#!/usr/bin/env python3
"""Auto-fix grader files for Derby 10.17"""

import re

files_to_fix = [
    'fully_automated_grader.py',
    'ultimate_autograder.py'
]

for filename in files_to_fix:
    print(f"\nFixing {filename}...")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix 1: Change driver class name
        old_driver = "org.apache.derby.jdbc.EmbeddedDriver"
        new_driver = "org.apache.derby.iapi.jdbc.AutoloadedDriver"
        
        count = content.count(old_driver)
        content = content.replace(old_driver, new_driver)
        print(f"  ✓ Changed driver class ({count} occurrences)")
        
        # Fix 2: Add JVM initialization at top of file (after imports)
        if "initialize_jvm_with_derby" not in content:
            jvm_init = '''
# ========================================
# CRITICAL: Initialize JVM with Derby JAR
# ========================================
import jpype

def initialize_jvm_with_derby():
    """Initialize JVM and add Derby JAR to classpath"""
    if jpype.isJVMStarted():
        return True
    
    if not os.environ.get('JAVA_HOME'):
        os.environ['JAVA_HOME'] = r'C:\\Program Files\\Java\\jdk-21'
    
    derby_jar = r"C:\\Derby\\lib\\derby.jar"
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

'''
            # Insert after the imports (before first class definition)
            class_match = re.search(r'^class \w+', content, re.MULTILINE)
            if class_match:
                insert_pos = class_match.start()
                content = content[:insert_pos] + jvm_init + content[insert_pos:]
                print(f"  ✓ Added JVM initialization")
        
        # Fix 3: Remove derby_jar parameter from jaydebeapi.connect()
        # Pattern: jaydebeapi.connect(..., [derby_jar]) or jaydebeapi.connect(..., derby_jar)
        content = re.sub(
            r'(jaydebeapi\.connect\([^)]+\[\"[^"]*\",\s*\"[^"]*\"\],)\s*\[?derby_jar\]?\s*(\))',
            r'\1\2',
            content
        )
        print(f"  ✓ Removed derby_jar parameter from connect() calls")
        
        # Write fixed file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ {filename} fixed successfully!")
        
    except Exception as e:
        print(f"  ✗ Error fixing {filename}: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*70)
print("BOTH FILES FIXED!")
print("="*70)
print("\nNow run:")
print("  $env:JAVA_HOME = 'C:\\Program Files\\Java\\jdk-21'")
print("  python .\\ultimate_autograder.py project.zip database.zip 2")