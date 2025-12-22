#!/usr/bin/env python3
"""Test Derby connection - USING addClassPath"""

import os
import sys
import jpype
import jaydebeapi
import tempfile
import shutil

print("=" * 60)
print("DERBY CONNECTION TEST - addClassPath Method")
print("=" * 60)

# Setup
derby_jar = r"C:\Derby\lib\derby.jar"
java_home = r"C:\Program Files\Java\jdk-21"
os.environ['JAVA_HOME'] = java_home

print(f"\n1. Derby JAR: {derby_jar}")
print(f"   Exists: {os.path.exists(derby_jar)}")

# Start JVM first (without Derby)
print("\n2. Starting JVM...")
if not jpype.isJVMStarted():
    jvm_path = os.path.join(java_home, 'bin', 'server', 'jvm.dll')
    jpype.startJVM(jvm_path, convertStrings=False)
    print("   ✓ JVM started")

# Add Derby JAR to classpath using addClassPath
print("\n3. Adding Derby JAR to JVM classpath...")
jpype.addClassPath(derby_jar)
print("   ✓ Derby JAR added to classpath")

# Try loading the Derby driver class directly
print("\n4. Testing if Derby driver class can be loaded...")
try:
    DerbyDriver = jpype.JClass("org.apache.derby.jdbc.EmbeddedDriver")
    print(f"   ✓ Derby driver class loaded: {DerbyDriver}")
except Exception as e:
    print(f"   ✗ Cannot load Derby driver class: {e}")

# Now connect with jaydebeapi (no need to pass derby_jar since it's in classpath)
print("\n5. Connecting to Derby...")
try:
    test_db = os.path.join(tempfile.gettempdir(), "test_derby_db")
    
    conn = jaydebeapi.connect(
        "org.apache.derby.jdbc.EmbeddedDriver",
        f"jdbc:derby:{test_db};create=true",
        ["", ""]
        # NO derby_jar parameter - it's already in classpath!
    )
    print("   ✓✓✓ CONNECTION SUCCESSFUL! ✓✓✓")
    
    # Test a query
    cursor = conn.cursor()
    cursor.execute("VALUES(1)")
    result = cursor.fetchone()
    print(f"   ✓ Test query result: {result[0]}")
    
    conn.close()
    print("   ✓ Connection closed")
    
    # Cleanup
    if os.path.exists(test_db):
        shutil.rmtree(test_db)
        print("   ✓ Test database cleaned up")
    
    print("\n" + "="*60)
    print("SUCCESS! This method works!")
    print("="*60)
    
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()