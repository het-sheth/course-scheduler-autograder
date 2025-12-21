# Testing the Auto-Grader

This document helps you test the auto-grader before using it on real student submissions.

## Quick Test (2 minutes)

### Option 1: Use Existing Student Submission

If you have a sample/reference submission from a previous semester:

```bash
python3 course_scheduler_autograder.py \
    sample_submission/project.zip \
    sample_submission/database.zip \
    1
```

Expected: Should complete without errors and generate a report.

### Option 2: Create Minimal Test Case

Create a test database manually:

```bash
# Create a minimal Derby database structure
mkdir -p test_db/CourseSchedulerDBTest
cd test_db/CourseSchedulerDBTest

# Create basic Derby structure
mkdir -p log seg0

# Create service.properties
cat > service.properties << 'EOF'
derby.serviceProtocol=
derby.serviceMaster=
derby.authentication.provider=BUILTIN
derby.database.propertiesOnly=false
EOF

# This creates a minimal Derby database that the grader can connect to
# (Note: This won't have tables - you'll see deductions for missing tables)
```

## Comprehensive Testing

### Test Case 1: Valid Submission (Should get 65/100)

**Setup:**
- Complete NetBeans project with all source files
- Derby database with all 5 tables (empty)
- Uses PreparedStatements in code

**Expected Result:**
```
Database Structure: 55 pts
Code Quality: 10 pts
Total: 65/100 (automatic portion)
Comments: Functional tests require manual verification
```

### Test Case 2: Missing Tables (Should get 15/100)

**Setup:**
- Database with only 2 tables instead of 5

**Expected Result:**
```
Deductions:
  -30 pts: Missing tables: CLASSES, STUDENTS, SCHEDULE
Total: 25/100
```

### Test Case 3: Non-Empty Database (Should lose 5 pts)

**Setup:**
- All tables exist
- Tables contain data

**Expected Result:**
```
Deductions:
  -5 pts: Tables not empty: SEMESTER, COURSES
```

### Test Case 4: No PreparedStatements (Should lose 10 pts)

**Setup:**
- Uses string concatenation instead of PreparedStatements

**Expected Result:**
```
Deductions:
  -10 pts: Does not use PreparedStatements
```

## Batch Grader Testing

Create a test submissions directory:

```bash
mkdir -p test_submissions

# Create 3 test student folders
for student in Student1 Student2 Student3; do
    mkdir -p test_submissions/$student
    # Copy sample submissions or create dummy ones
done

# Run batch grader
python3 batch_grader.py test_submissions/ test_results/ 1
```

**Expected Output:**
- Individual JSON reports for each student
- CSV summary file
- HTML dashboard
- Console output showing progress

## Validation Checklist

Use this checklist to ensure the grader is working correctly:

### Installation Validation
- [ ] Python 3.8+ installed
- [ ] jaydebeapi package installed
- [ ] Derby JAR file found
- [ ] Setup script runs without errors

### Single Grading Validation
- [ ] Can extract ZIP files
- [ ] Can connect to Derby database
- [ ] Can find NetBeans project structure
- [ ] Can analyze Java source code
- [ ] Generates JSON report
- [ ] Console output is readable

### Batch Grading Validation
- [ ] Finds all student submissions
- [ ] Processes multiple students
- [ ] Generates individual reports
- [ ] Creates CSV summary
- [ ] Creates HTML dashboard
- [ ] Statistics are calculated correctly

### Report Validation
- [ ] JSON structure is valid
- [ ] Point allocations match rubric
- [ ] Deductions are logged
- [ ] Comments are helpful
- [ ] Total score calculated correctly

## Common Test Scenarios

### Scenario: Student submits wrong files

**Setup:** Put non-Derby database files in database.zip

**Expected:** Error message about database structure

**Test:**
```bash
# Create invalid database
mkdir invalid_db
echo "fake" > invalid_db/notadatabase.txt
zip -r invalid_db.zip invalid_db/

python3 course_scheduler_autograder.py project.zip invalid_db.zip 1
# Should show: "Database validation error: ..."
```

### Scenario: Corrupt ZIP file

**Setup:** Create corrupted ZIP

**Expected:** Clear error message

**Test:**
```bash
# Create corrupt ZIP
echo "not a zip" > corrupt.zip

python3 course_scheduler_autograder.py corrupt.zip database.zip 1
# Should show extraction error
```

### Scenario: Project without source code

**Setup:** Empty NetBeans project

**Expected:** Warning about missing source

**Test:**
```bash
# Create empty project structure
mkdir -p empty_project/src
zip -r empty_project.zip empty_project/

python3 course_scheduler_autograder.py empty_project.zip database.zip 1
# Should show: "Found 0 Java files"
```

## Performance Testing

Test with increasing numbers of submissions:

```bash
# Test with 1 student (~30 seconds)
time python3 batch_grader.py small_batch/ results/ 1

# Test with 10 students (~5 minutes)
time python3 batch_grader.py medium_batch/ results/ 1

# Test with 50 students (~25 minutes)
time python3 batch_grader.py large_batch/ results/ 1
```

**Expected performance:**
- ~30 seconds per student
- Linear scaling (10 students = ~5 minutes)
- Memory usage stays reasonable (<1GB)

## Regression Testing

After modifying the grader, run these tests:

```bash
# Save current results
python3 batch_grader.py test_submissions/ baseline_results/ 1
cp baseline_results/grading_summary_part1.csv baseline.csv

# Make your changes to the grader
# ...

# Test again
python3 batch_grader.py test_submissions/ new_results/ 1

# Compare results
diff baseline.csv new_results/grading_summary_part1.csv
# Should show only expected differences
```

## GUI Testing

Test the GUI interface:

```bash
python3 autograder_gui.py
```

**Test checklist:**
- [ ] Window opens correctly
- [ ] Browse buttons work
- [ ] File paths display correctly
- [ ] Radio buttons toggle
- [ ] Grade button starts processing
- [ ] Output appears in text area
- [ ] Progress bar animates (batch mode)
- [ ] Success/error messages appear
- [ ] Can grade multiple times without restart

## Troubleshooting Tests

If tests fail, run these diagnostics:

```bash
# Test Derby installation
find /usr -name "derby.jar"

# Test Python dependencies
python3 -c "import jaydebeapi; print('OK')"

# Test file permissions
ls -la /tmp/grading_workspace/

# Test with verbose output
python3 -u course_scheduler_autograder.py project.zip db.zip 1

# Check logs
cat /tmp/grading_workspace/*.log
```

## Success Criteria

The auto-grader is ready for production use when:

1. ✓ All validation tests pass
2. ✓ Can grade 10 submissions successfully
3. ✓ Reports are accurate and complete
4. ✓ Performance is acceptable
5. ✓ GUI works smoothly
6. ✓ No crashes or hangs
7. ✓ Error messages are helpful

## Final Pre-Production Test

Before using on real student submissions:

```bash
# 1. Run on sample submissions from previous semester
python3 batch_grader.py previous_semester/ test_results/ 1

# 2. Manually verify a few results
# Compare auto-grader scores with original grades

# 3. Check for consistency
# Same submission should get same score every time

# 4. Verify reports are complete
grep -r "total_points" test_results/*.json

# 5. Test both parts
python3 batch_grader.py part1_samples/ part1_results/ 1
python3 batch_grader.py part2_samples/ part2_results/ 2
```

If all tests pass → Ready for production! 🎉
