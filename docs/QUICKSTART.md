# Quick Start Guide

## Installation (5 minutes)

1. **Run setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Verify installation:**
   ```bash
   python3 course_scheduler_autograder.py --help
   ```

## Usage Scenarios

### Scenario 1: Grade a Single Student (Most Common)

You have two files from a student:
- `CourseSchedulerJohnSmithjds123.zip` (project)
- `CourseSchedulerDBJohnSmithjds123.zip` (database)

**Command:**
```bash
python3 course_scheduler_autograder.py \
    CourseSchedulerJohnSmithjds123.zip \
    CourseSchedulerDBJohnSmithjds123.zip \
    1
```

**What happens:**
- Extracts both zips
- Validates database structure
- Checks code quality
- Generates grading report

**Output:**
- Console: Detailed grading results
- File: `/tmp/grading_workspace/grading_report.json`

**Time:** ~30 seconds

---

### Scenario 2: Grade Multiple Students (Batch Mode)

You have a folder with multiple student submissions:

```
submissions/
├── JohnSmith/
│   ├── CourseScheduler...zip
│   └── CourseSchedulerDB...zip
├── JaneDoe/
│   ├── CourseScheduler...zip
│   └── CourseSchedulerDB...zip
└── BobJones/
    ├── CourseScheduler...zip
    └── CourseSchedulerDB...zip
```

**Command:**
```bash
python3 batch_grader.py submissions/ grading_reports/ 1
```

**What happens:**
- Processes all students automatically
- Generates individual reports
- Creates summary CSV
- Creates HTML dashboard

**Output:**
```
grading_reports/
├── JohnSmith_report.json
├── JaneDoe_report.json
├── BobJones_report.json
├── grading_summary_part1.csv      ← Open in Excel
└── grading_summary_part1.html     ← Open in browser
```

**Time:** ~30 seconds per student

---

### Scenario 3: Use GUI Interface (Easiest)

**Command:**
```bash
python3 autograder_gui.py
```

**Steps:**
1. Click "Browse" next to "Project ZIP"
2. Select the student's project zip file
3. Click "Browse" next to "Database ZIP"
4. Select the student's database zip file
5. Select "Part 1" or "Part 2"
6. Click "Grade Submission"
7. View results in the output window

**For Batch Grading:**
1. Switch to "Batch Grading" tab
2. Select submissions folder
3. Select output folder
4. Click "Grade All Submissions"
5. View progress and results

---

## Understanding the Results

### Automated Scoring

The tool automatically checks:
- ✓ Database exists and connects
- ✓ All 5 required tables exist (50 pts)
- ✓ Tables are empty (5 pts)
- ✓ Uses PreparedStatements (10 pts)
- ✗ SQL injection vulnerabilities (deduction)

**Typical automatic score:** 65/100 points

### Manual Verification Required

You still need to manually test:
- GUI functionality (11 pts)
- Add/Display operations (75 pts)
- Combo boxes and user interaction

**Recommended approach:**
1. Run auto-grader first → get database/code score
2. Run the project manually → test functionality
3. Combine scores for final grade

---

## Common Workflows

### Workflow 1: Weekly Grading (Teaching Assistant)

```bash
# Monday: Students submit assignments
# Tuesday morning: Download all submissions

# Organize submissions
mkdir week12_submissions
cd week12_submissions
# ... move student folders here ...

# Run batch grader
cd ..
python3 batch_grader.py week12_submissions/ week12_grades/ 1

# Review results
open week12_grades/grading_summary_part1.html

# Manual testing for functionality
# ... test each student's GUI ...

# Export to gradebook
# Use week12_grades/grading_summary_part1.csv
```

### Workflow 2: Individual Student Regrade

```bash
# Student requests regrade
# Download their resubmission

python3 course_scheduler_autograder.py \
    resubmission/project.zip \
    resubmission/database.zip \
    1

# Review report
cat /tmp/grading_workspace/grading_report.json | jq .
```

### Workflow 3: Final Project Grading (Instructor)

```bash
# Part 1 (Week 1)
python3 batch_grader.py submissions_part1/ grades_part1/ 1

# Part 2 (Week 2)  
python3 batch_grader.py submissions_part2/ grades_part2/ 2

# Combine scores
# ... merge CSV files ...
```

---

## Troubleshooting One-Liners

**Derby not found:**
```bash
find /usr -name "derby.jar" 2>/dev/null
```

**Check student's database:**
```bash
unzip -l database.zip | grep -E "(log|service.properties)"
```

**View JSON report nicely:**
```bash
cat grading_report.json | python3 -m json.tool
```

**Quick test of installation:**
```bash
python3 -c "import jaydebeapi; print('✓ JayDeBeApi installed')"
```

---

## Tips for Efficient Grading

1. **Use batch mode** for initial automated checks
2. **Sort by score** to identify problem submissions
3. **Check CSV first** for overview
4. **Use HTML dashboard** for detailed review
5. **Manual test** only functionality (GUI)

## Getting Help

- Check full `README.md` for detailed documentation
- Review rubric files for point allocations
- Test with sample submission first
- Contact course instructor for rubric questions
