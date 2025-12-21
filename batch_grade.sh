#!/bin/bash
# Batch Grading Script for Course Scheduler
# Automatically grades all student submissions

set -e  # Exit on error

# Configuration
SUBMISSIONS_DIR="${1:-submissions}"
OUTPUT_DIR="${2:-grading_results}"
PART="${3:-1}"
GRADER="${4:-ultimate_autograder.py}"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Course Scheduler Batch Grading"
echo "=========================================="
echo ""
echo "Submissions: $SUBMISSIONS_DIR"
echo "Output: $OUTPUT_DIR"
echo "Part: $PART"
echo "Grader: $GRADER"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Counter
total=0
successful=0
failed=0

# Find all student directories
for student_dir in "$SUBMISSIONS_DIR"/*/ ; do
    if [ ! -d "$student_dir" ]; then
        continue
    fi
    
    student_name=$(basename "$student_dir")
    echo -e "${YELLOW}Processing: $student_name${NC}"
    
    # Find project and database files
    project=$(find "$student_dir" -type f -name "*.zip" ! -name "*DB*" ! -name "*database*" | head -n 1)
    database=$(find "$student_dir" -type f -name "*DB*.zip" -o -name "*database*.zip" | head -n 1)
    
    if [ -z "$project" ] || [ -z "$database" ]; then
        echo -e "${RED}  ✗ Missing files for $student_name${NC}"
        echo "  Project: $project"
        echo "  Database: $database"
        ((failed++))
        continue
    fi
    
    echo "  Project: $(basename "$project")"
    echo "  Database: $(basename "$database")"
    
    # Grade the submission
    output_file="$OUTPUT_DIR/${student_name}_grade.txt"
    
    if python3 "$GRADER" "$project" "$database" "$PART" > "$output_file" 2>&1; then
        # Extract grade from output
        grade=$(grep "FINAL GRADE:" "$output_file" | tail -n 1 || echo "Unknown")
        score=$(grep "TOTAL SCORE" "$output_file" | grep -oP '\d+(?=/\d+)' || echo "?")
        
        echo -e "${GREEN}  ✓ Complete: $grade (Score: $score/100)${NC}"
        ((successful++))
    else
        echo -e "${RED}  ✗ Failed to grade${NC}"
        ((failed++))
    fi
    
    ((total++))
    echo ""
done

# Summary
echo "=========================================="
echo "Grading Summary"
echo "=========================================="
echo -e "Total students: $total"
echo -e "${GREEN}Successful: $successful${NC}"
echo -e "${RED}Failed: $failed${NC}"
echo ""
echo "Results saved in: $OUTPUT_DIR/"
echo ""

# Generate summary CSV
echo "Generating summary CSV..."
summary_file="$OUTPUT_DIR/summary.csv"

echo "Student,Score,Grade,Status" > "$summary_file"

for grade_file in "$OUTPUT_DIR"/*_grade.txt; do
    if [ -f "$grade_file" ]; then
        student=$(basename "$grade_file" _grade.txt)
        score=$(grep "TOTAL SCORE" "$grade_file" | grep -oP '\d+(?=/\d+)' || echo "0")
        grade=$(grep "FINAL GRADE:" "$grade_file" | grep -oP '(?<=: )[A-F][+-]?' || echo "F")
        
        if grep -q "GRADING COMPLETE" "$grade_file"; then
            status="Success"
        else
            status="Failed"
        fi
        
        echo "$student,$score,$grade,$status" >> "$summary_file"
    fi
done

echo -e "${GREEN}✓ Summary saved to: $summary_file${NC}"
echo ""

# Open summary if possible
if command -v xdg-open &> /dev/null; then
    echo "Opening summary..."
    xdg-open "$summary_file" 2>/dev/null || true
elif command -v open &> /dev/null; then
    echo "Opening summary..."
    open "$summary_file" 2>/dev/null || true
fi

echo "Done!"
