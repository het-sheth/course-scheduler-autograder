# Example Submission Structure

This file shows you how to organize student submissions for batch grading.

## For Single Student Grading

Just have the two files in any location:
```
CourseSchedulerJohnSmithjds123.zip
CourseSchedulerDBJohnSmithjds123.zip
```

## For Batch Grading

Organize submissions in folders like this:

```
submissions/
│
├── JohnSmith_jds123/
│   ├── CourseSchedulerJohnSmithjds123.zip
│   └── CourseSchedulerDBJohnSmithjds123.zip
│
├── JaneDoe_jad456/
│   ├── CourseSchedulerJaneDoeJad456.zip
│   └── CourseSchedulerDBJaneDoeJad456.zip
│
├── BobJones_rbj789/
│   ├── CourseSchedulerBobJonesrbj789.zip
│   └── CourseSchedulerDBBobJonesrbj789.zip
│
└── AliceWilliams_aew012/
    ├── CourseSchedulerAliceWilliamsaew012.zip
    └── CourseSchedulerDBAliceWilliamsaew012.zip
```

## Important Notes

1. **Each student gets their own folder**
   - Folder name doesn't matter (e.g., "JohnSmith_jds123" or just "jds123")
   - Helps keep submissions organized

2. **Each folder must contain exactly 2 files:**
   - One project ZIP (containing the NetBeans project)
   - One database ZIP (containing the Derby database)

3. **File naming:**
   - Project should start with "CourseScheduler" or contain "project"
   - Database should start with "CourseSchedulerDB" or contain "database" or "DB"
   - Examples:
     ✓ CourseSchedulerJohnSmithjds123.zip
     ✓ jds123_project.zip
     ✓ CourseScheduler_jds123.zip
     ✓ CourseSchedulerDBJohnSmithjds123.zip
     ✓ jds123_database.zip
     ✓ jds123_DB.zip

## Downloading from Canvas

If you're downloading from Canvas LMS:

1. **Bulk Download:**
   - Go to Assignments → [Assignment Name]
   - Click "Download Submissions"
   - Canvas creates: `submissions.zip`

2. **Extract:**
   ```bash
   unzip submissions.zip
   ```

3. **Reorganize if needed:**
   Canvas usually creates folders like:
   ```
   StudentName_123456_assignsubmission_file_/
       CourseScheduler...zip
       CourseSchedulerDB...zip
   ```
   
   This structure works fine with the batch grader!

## Alternative: Flat Structure

If you prefer, you can also use a flat structure with naming conventions:

```
submissions/
├── jds123_CourseScheduler.zip
├── jds123_CourseSchedulerDB.zip
├── jad456_CourseScheduler.zip
├── jad456_CourseSchedulerDB.zip
├── rbj789_CourseScheduler.zip
└── rbj789_CourseSchedulerDB.zip
```

Then create folders:
```bash
cd submissions
for id in jds123 jad456 rbj789; do
    mkdir -p $id
    mv ${id}_*.zip $id/
done
```

## Testing Your Structure

Before running batch grader, verify structure:

```bash
# Check folder structure
ls -R submissions/

# Count submissions (should be number of students)
find submissions/ -name "*.zip" | wc -l
# Result should be: 2 * number_of_students

# Verify each student has 2 files
for dir in submissions/*/; do
    count=$(find "$dir" -maxdepth 1 -name "*.zip" | wc -l)
    if [ $count -ne 2 ]; then
        echo "WARNING: $dir has $count files (should be 2)"
    fi
done
```

## Quick Setup Script

Save this as `organize_submissions.sh`:

```bash
#!/bin/bash
# Organize Canvas bulk download into proper structure

DOWNLOAD_ZIP="$1"  # submissions.zip from Canvas
OUTPUT_DIR="organized_submissions"

if [ -z "$DOWNLOAD_ZIP" ]; then
    echo "Usage: ./organize_submissions.sh submissions.zip"
    exit 1
fi

# Extract Canvas download
mkdir -p temp_extract
unzip "$DOWNLOAD_ZIP" -d temp_extract

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Find all project/database pairs and organize
cd temp_extract
for student_dir in */; do
    student_name=$(basename "$student_dir")
    
    # Find the two zip files
    project=$(find "$student_dir" -name "CourseScheduler*.zip" ! -name "*DB*.zip" | head -1)
    database=$(find "$student_dir" -name "CourseScheduler*DB*.zip" | head -1)
    
    if [ -n "$project" ] && [ -n "$database" ]; then
        # Create student folder
        mkdir -p "../$OUTPUT_DIR/$student_name"
        
        # Copy files
        cp "$project" "../$OUTPUT_DIR/$student_name/"
        cp "$database" "../$OUTPUT_DIR/$student_name/"
        
        echo "✓ Organized: $student_name"
    else
        echo "⚠ Skipped: $student_name (missing files)"
    fi
done

cd ..
rm -rf temp_extract

echo ""
echo "✓ Organization complete!"
echo "Ready to grade: python3 batch_grader.py $OUTPUT_DIR/ grading_results/ 1"
```

Usage:
```bash
chmod +x organize_submissions.sh
./organize_submissions.sh submissions.zip
```
