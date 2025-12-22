#!/usr/bin/env python3
"""Test with the correct Derby driver class"""

import os
import sys
import jpype
import jaydebeapi
import tempfile
import shutil

print("=" * 70)
print("TESTING CORRECT DERBY DRIVER CLASS")
print("=" * 70)

derby_jar = r"C:\Derby\lib\derby.jar"
java_home = r"C:\Program Files\Java\jdk-21"
os.environ['JAVA_HOME'] = java_home

# Start JVM
if not jpype.isJVMStarted():
    jvm_path = os.path.join(java_home, 'bin', 'server', 'jvm.dll')
    jpype.startJVM(jvm_path, convertStrings=False)
    jpype.addClassPath(derby_jar)
    print("✓ JVM started with Derby JAR")

# Test different driver class names
driver_classes = [
    "org.apache.derby.jdbc.AutoloadedDriver",
    "org.apache.derby.iapi.jdbc.AutoloadedDriver",
    "org.apache.derby.jdbc.EmbeddedDriver40",
]

print(f"\nTesting different Derby driver classes:")
for driver_name in driver_classes:
    try:
        print(f"\n  Trying: {driver_name}")
        DriverClass = jpype.JClass(driver_name)
        print(f"    ✓✓✓ SUCCESS! Class loaded: {DriverClass}")
        
        # Try connecting with this driver
        print(f"    Testing connection...")
        test_db = os.path.join(tempfile.gettempdir(), "test_derby_db")
        
        conn = jaydebeapi.connect(
            driver_name,  # Use the working driver name
            f"jdbc:derby:{test_db};create=true",
            ["", ""]
        )
        print(f"    ✓✓✓ CONNECTION SUCCESSFUL with {driver_name}!")
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("VALUES(1)")
        result = cursor.fetchone()
        print(f"    ✓ Query result: {result[0]}")
        
        conn.close()
        
        # Cleanup
        if os.path.exists(test_db):
            shutil.rmtree(test_db)
        
        print(f"\n" + "="*70)
        print(f"SUCCESS! Use this driver: {driver_name}")
        print("="*70)
        break  # Stop after first success
        
    except Exception as e:
        print(f"    ✗ Failed: {e}")

print("\n" + "="*70)