#!/bin/bash
# Setup script for Course Scheduler Auto-Grader

echo "Course Scheduler Auto-Grader Setup"
echo "===================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Error: Python 3 not found"; exit 1; }
echo "✓ Python 3 found"
echo ""

# Check Java
echo "Checking Java..."
java -version 2>&1 | head -n 1 || { echo "Error: Java not found"; exit 1; }
echo "✓ Java found"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt
echo "✓ Python dependencies installed"
echo ""

# Check for Derby
echo "Checking for Apache Derby..."
DERBY_JAR=$(find /usr -name "derby.jar" 2>/dev/null | head -n 1)

if [ -z "$DERBY_JAR" ]; then
    echo "⚠ Apache Derby not found in /usr"
    echo ""
    echo "Please install Apache Derby:"
    echo "  Ubuntu/Debian: sudo apt-get install libderby-java"
    echo "  Or download from: https://db.apache.org/derby/"
    echo ""
    echo "After installation, update the derby_jar path in:"
    echo "  course_scheduler_autograder.py"
    echo ""
else
    echo "✓ Derby found at: $DERBY_JAR"
    echo ""
    echo "Updating course_scheduler_autograder.py..."
    sed -i "s|derby_jar = \"/usr/share/java/derby.jar\"|derby_jar = \"$DERBY_JAR\"|" course_scheduler_autograder.py
    echo "✓ Derby path updated"
fi

echo ""
echo "Setup complete!"
echo ""
echo "Usage:"
echo "  Single submission:"
echo "    python3 course_scheduler_autograder.py <project.zip> <database.zip> [part]"
echo ""
echo "  Batch grading:"
echo "    python3 batch_grader.py <submissions_dir> <output_dir> [part]"
echo ""
echo "See README.md for detailed documentation"
