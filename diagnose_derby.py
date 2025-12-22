#!/usr/bin/env python3
"""Complete Derby JAR diagnostic"""

import os
import zipfile
import subprocess

print("=" * 70)
print("COMPLETE DERBY JAR DIAGNOSTIC")
print("=" * 70)

derby_jar = r"C:\Derby\lib\derby.jar"
java_home = r"C:\Program Files\Java\jdk-21"

# Test 1: Basic file info
print(f"\n1. Derby JAR File Info:")
print(f"   Path: {derby_jar}")
print(f"   Exists: {os.path.exists(derby_jar)}")
print(f"   Size: {os.path.getsize(derby_jar):,} bytes")
print(f"   Readable: {os.access(derby_jar, os.R_OK)}")

# Test 2: Is it a valid ZIP/JAR?
print(f"\n2. JAR File Integrity:")
try:
    with zipfile.ZipFile(derby_jar, 'r') as jar:
        files = jar.namelist()
        print(f"   ✓ Valid ZIP/JAR file")
        print(f"   Total files in JAR: {len(files)}")
        
        # Test 3: Look for Derby driver class
        print(f"\n3. Searching for Derby Driver Class:")
        driver_class = "org/apache/derby/jdbc/EmbeddedDriver.class"
        
        if driver_class in files:
            print(f"   ✓ FOUND: {driver_class}")
            info = jar.getinfo(driver_class)
            print(f"   File size: {info.file_size} bytes")
            print(f"   Compressed: {info.compress_size} bytes")
        else:
            print(f"   ✗ NOT FOUND: {driver_class}")
            
            # Search for anything with "Driver" in the name
            print(f"\n   Searching for any Driver classes:")
            driver_files = [f for f in files if 'Driver' in f and f.endswith('.class')]
            if driver_files:
                print(f"   Found {len(driver_files)} Driver classes:")
                for df in driver_files[:10]:  # Show first 10
                    print(f"     - {df}")
            else:
                print(f"   ✗ No Driver classes found at all!")
        
        # Test 4: Look for Derby-specific classes
        print(f"\n4. Looking for Derby classes:")
        derby_classes = [f for f in files if f.startswith('org/apache/derby/') and f.endswith('.class')]
        print(f"   Found {len(derby_classes)} Derby classes")
        if derby_classes:
            print(f"   Examples:")
            for dc in derby_classes[:5]:
                print(f"     - {dc}")
        
        # Test 5: Check META-INF
        print(f"\n5. Checking META-INF:")
        manifest = [f for f in files if f.startswith('META-INF/')]
        if manifest:
            print(f"   Found {len(manifest)} META-INF files:")
            for mf in manifest[:10]:
                print(f"     - {mf}")
                
            # Try to read MANIFEST.MF
            if 'META-INF/MANIFEST.MF' in files:
                print(f"\n   Reading MANIFEST.MF:")
                manifest_content = jar.read('META-INF/MANIFEST.MF').decode('utf-8', errors='ignore')
                print(f"   {manifest_content[:500]}")  # First 500 chars
        
except Exception as e:
    print(f"   ✗ ERROR reading JAR: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Try using Java directly to test the JAR
print(f"\n6. Testing Derby JAR with Java directly:")
try:
    java_exe = os.path.join(java_home, 'bin', 'java.exe')
    
    # Try to get Derby version/sysinfo
    result = subprocess.run(
        [java_exe, '-cp', derby_jar, 'org.apache.derby.tools.sysinfo'],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.returncode == 0:
        print(f"   ✓ Derby sysinfo ran successfully!")
        print(f"   Output (first 500 chars):")
        print(f"   {result.stdout[:500]}")
    else:
        print(f"   ✗ Derby sysinfo failed")
        print(f"   Error: {result.stderr[:300]}")
        
except subprocess.TimeoutExpired:
    print(f"   ⚠ Timeout (but Derby might be working)")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 7: Check if this is the right Derby JAR
print(f"\n7. Identifying Derby JAR type:")
derby_dir = os.path.dirname(os.path.dirname(derby_jar))
print(f"   Derby directory: {derby_dir}")
print(f"   Contents of Derby lib folder:")
try:
    lib_dir = os.path.dirname(derby_jar)
    for item in os.listdir(lib_dir):
        if item.endswith('.jar'):
            jar_path = os.path.join(lib_dir, item)
            size = os.path.getsize(jar_path)
            print(f"     - {item} ({size:,} bytes)")
except Exception as e:
    print(f"   ✗ Error listing: {e}")

print("\n" + "=" * 70)
print("DIAGNOSIS COMPLETE")
print("=" * 70)