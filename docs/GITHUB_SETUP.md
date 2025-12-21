# GitHub Setup Guide - Course Scheduler Auto-Grader

## Quick Start (5 minutes)

### Step 1: Create Local Project

```bash
# Create project directory
mkdir course-scheduler-autograder
cd course-scheduler-autograder

# Initialize git repository
git init

# Create project structure
mkdir -p docs examples scripts
```

### Step 2: Add Files

Place all your downloaded files in the project root:

```
course-scheduler-autograder/
├── ultimate_autograder.py
├── fully_automated_grader.py
├── course_scheduler_autograder.py
├── test_script_executor.py
├── advanced_code_analyzer.py
├── batch_grader.py
├── autograder_gui.py
├── requirements.txt
├── setup.sh
├── README.md
├── LICENSE
├── .gitignore
└── docs/
    ├── QUICKSTART.md
    ├── INSTALLATION.md
    └── EXAMPLES.md
```

### Step 3: Create GitHub Repository

**Option A: Via GitHub Website**
1. Go to https://github.com
2. Click "New" or "+" → "New repository"
3. Name: `course-scheduler-autograder`
4. Description: "Automated grading tool for Java Course Scheduler projects with 100% automation"
5. Public ✓
6. Don't initialize with README (we have our own)
7. Click "Create repository"

**Option B: Via GitHub CLI (if installed)**
```bash
gh repo create course-scheduler-autograder --public --description "Automated grading tool for Java Course Scheduler projects"
```

### Step 4: Connect Local to GitHub

```bash
# Add all files
git add .

# Initial commit
git commit -m "Initial commit: Course Scheduler Auto-Grader v1.0"

# Connect to GitHub (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/course-scheduler-autograder.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 5: Keep Updating

```bash
# Make changes to your files
# Then:

git add .
git commit -m "Description of your changes"
git push
```

---

## Recommended Project Structure

```
course-scheduler-autograder/
│
├── README.md                           # Main documentation
├── LICENSE                             # MIT or appropriate license
├── requirements.txt                    # Python dependencies
├── setup.sh                           # Installation script
├── .gitignore                         # Files to ignore
│
├── src/                               # Source code
│   ├── ultimate_autograder.py
│   ├── fully_automated_grader.py
│   ├── course_scheduler_autograder.py
│   ├── test_script_executor.py
│   ├── advanced_code_analyzer.py
│   ├── batch_grader.py
│   └── autograder_gui.py
│
├── docs/                              # Documentation
│   ├── INSTALLATION.md
│   ├── QUICKSTART.md
│   ├── USAGE.md
│   ├── 100_PERCENT_AUTOMATED.md
│   └── TROUBLESHOOTING.md
│
├── examples/                          # Example files
│   ├── sample_submission/
│   │   ├── project.zip
│   │   └── database.zip
│   └── example_output/
│       ├── grading_report.json
│       └── grading_report.txt
│
├── tests/                            # Test files
│   ├── test_database.py
│   └── test_grader.py
│
└── scripts/                          # Helper scripts
    ├── batch_grade.sh
    └── setup_derby.sh
```

---

## Common Git Commands

### Daily Workflow

```bash
# Check status
git status

# See what changed
git diff

# Add specific files
git add filename.py

# Add all changes
git add .

# Commit changes
git commit -m "Fixed bug in waitlist logic"

# Push to GitHub
git push

# Pull latest changes (if working with others)
git pull
```

### Branching (Optional but Recommended)

```bash
# Create new feature branch
git checkout -b feature/new-functionality

# Make changes, commit
git add .
git commit -m "Added new feature"

# Push branch to GitHub
git push -u origin feature/new-functionality

# Switch back to main
git checkout main

# Merge feature when ready
git merge feature/new-functionality
```

### Tagging Releases

```bash
# Create version tag
git tag -a v1.0.0 -m "Version 1.0.0 - Initial release"

# Push tags to GitHub
git push origin --tags
```

---

## Best Practices

### 1. Meaningful Commit Messages

**Good:**
```bash
git commit -m "Add support for Part 2 test scripts"
git commit -m "Fix database connection timeout issue"
git commit -m "Update README with installation instructions"
```

**Bad:**
```bash
git commit -m "fixes"
git commit -m "update"
git commit -m "changes"
```

### 2. Commit Often

Don't wait to make huge commits. Commit logical chunks:
```bash
# After fixing a bug
git commit -m "Fix: Prevent SQL injection in student ID query"

# After adding a feature
git commit -m "Add: GUI button for batch processing"

# After documentation
git commit -m "Docs: Add troubleshooting section for Derby errors"
```

### 3. Use .gitignore

Don't commit:
- Compiled files (`.pyc`, `.class`)
- Virtual environments (`venv/`, `env/`)
- IDE files (`.idea/`, `.vscode/`)
- OS files (`.DS_Store`, `Thumbs.db`)
- Test outputs (`/tmp/`, `*.log`)

---

## GitHub Features to Enable

### 1. GitHub Actions (CI/CD)

Create `.github/workflows/test.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python -m pytest tests/
```

### 2. GitHub Pages (Documentation)

Enable in Settings → Pages → Source: `main` branch, `/docs` folder

### 3. Issues & Projects

Enable in Settings → Features:
- ✓ Issues (for bug tracking)
- ✓ Projects (for roadmap)
- ✓ Wiki (for extended docs)

---

## Collaboration Workflow

### If Working with Others

```bash
# Before starting work
git pull

# Create feature branch
git checkout -b feature/your-feature

# Make changes
git add .
git commit -m "Add feature description"

# Push your branch
git push -u origin feature/your-feature

# Create Pull Request on GitHub
# After review and approval, merge via GitHub
```

### Keeping Fork Updated (if you forked)

```bash
# Add upstream remote
git remote add upstream https://github.com/ORIGINAL/course-scheduler-autograder.git

# Fetch updates
git fetch upstream

# Merge into your main
git checkout main
git merge upstream/main

# Push to your fork
git push origin main
```

---

## Making Releases

### Create a Release on GitHub

1. Go to repository → Releases → "Create a new release"
2. Tag version: `v1.0.0`
3. Release title: `Version 1.0.0 - Initial Release`
4. Description:
   ```markdown
   ## Features
   - 100% automated grading
   - Database validation
   - Code analysis
   - Test script execution
   
   ## Installation
   See README.md
   
   ## Usage
   `python3 ultimate_autograder.py project.zip database.zip 1`
   ```
5. Attach compiled files (if any)
6. Click "Publish release"

---

## Advanced: Automating with GitHub Actions

Create `.github/workflows/release.yml`:

```yaml
name: Build Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
```

---

## Troubleshooting

### Issue: Large files won't push

```bash
# GitHub has 100MB file limit
# Use Git LFS for large files

git lfs install
git lfs track "*.zip"
git add .gitattributes
git commit -m "Add Git LFS tracking"
```

### Issue: Accidentally committed sensitive data

```bash
# Remove from history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/file" \
  --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all
```

### Issue: Merge conflicts

```bash
# Pull latest
git pull

# Git will mark conflicts in files
# Edit files to resolve
# Then:
git add .
git commit -m "Resolve merge conflicts"
git push
```

---

## Summary: Complete Setup Commands

```bash
# 1. Create project
mkdir course-scheduler-autograder
cd course-scheduler-autograder
git init

# 2. Add your files
# (copy all .py files, .md files, etc. here)

# 3. Create .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
*$py.class
venv/
env/
.env
*.log
/tmp/
.DS_Store
.idea/
.vscode/
EOF

# 4. Initial commit
git add .
git commit -m "Initial commit: Course Scheduler Auto-Grader"

# 5. Create GitHub repo (via website or CLI)
# Then connect:
git remote add origin https://github.com/YOUR_USERNAME/course-scheduler-autograder.git
git branch -M main
git push -u origin main

# 6. Future updates
git add .
git commit -m "Your update message"
git push
```

That's it! Your project is now on GitHub and ready to share! 🚀
