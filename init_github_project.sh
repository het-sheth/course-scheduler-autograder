#!/bin/bash
# Quick GitHub Project Setup Script
# Run this to set up your GitHub repository in seconds!

set -e

echo "=========================================="
echo "Course Scheduler Auto-Grader"
echo "GitHub Project Setup"
echo "=========================================="
echo ""

# Get user info
read -p "Enter your GitHub username: " GITHUB_USER
read -p "Enter your name for LICENSE: " AUTHOR_NAME
read -p "Enter your email (optional): " AUTHOR_EMAIL

PROJECT_NAME="course-scheduler-autograder"

echo ""
echo "Setting up project: $PROJECT_NAME"
echo ""

# Create project directory
if [ ! -d "$PROJECT_NAME" ]; then
    mkdir "$PROJECT_NAME"
    echo "✓ Created project directory"
else
    echo "⚠ Project directory already exists"
fi

cd "$PROJECT_NAME"

# Initialize git
if [ ! -d ".git" ]; then
    git init
    echo "✓ Initialized git repository"
else
    echo "⚠ Git already initialized"
fi

# Create directory structure
mkdir -p docs examples scripts tests
echo "✓ Created directory structure"

# Copy files from downloads
echo ""
echo "Copy your downloaded files to this directory:"
echo "  $PWD"
echo ""
echo "Required files:"
echo "  - ultimate_autograder.py"
echo "  - fully_automated_grader.py"
echo "  - course_scheduler_autograder.py"
echo "  - test_script_executor.py"
echo "  - advanced_code_analyzer.py"
echo "  - batch_grader.py"
echo "  - autograder_gui.py"
echo "  - requirements.txt"
echo "  - setup.sh"
echo "  - .gitignore"
echo "  - README_GITHUB.md (rename to README.md)"
echo "  - LICENSE"
echo "  - CONTRIBUTING.md"
echo "  - GITHUB_SETUP.md"
echo ""

read -p "Press Enter when files are copied..."

# Move documentation files
if [ -f "GITHUB_SETUP.md" ]; then
    mv GITHUB_SETUP.md docs/ 2>/dev/null || true
fi

if [ -f "100_PERCENT_AUTOMATED.md" ]; then
    mv 100_PERCENT_AUTOMATED.md docs/ 2>/dev/null || true
fi

if [ -f "QUICKSTART.md" ]; then
    mv QUICKSTART.md docs/ 2>/dev/null || true
fi

# Rename README_GITHUB.md to README.md
if [ -f "README_GITHUB.md" ]; then
    mv README_GITHUB.md README.md
    echo "✓ Renamed README_GITHUB.md to README.md"
fi

# Update placeholders in files
if [ -f "README.md" ]; then
    sed -i "s/yourusername/$GITHUB_USER/g" README.md 2>/dev/null || \
    sed -i '' "s/yourusername/$GITHUB_USER/g" README.md 2>/dev/null || true
fi

if [ -f "LICENSE" ]; then
    sed -i "s/\[Your Name\]/$AUTHOR_NAME/g" LICENSE 2>/dev/null || \
    sed -i '' "s/\[Your Name\]/$AUTHOR_NAME/g" LICENSE 2>/dev/null || true
fi

if [ -f "CONTRIBUTING.md" ]; then
    sed -i "s/yourusername/$GITHUB_USER/g" CONTRIBUTING.md 2>/dev/null || \
    sed -i '' "s/yourusername/$GITHUB_USER/g" CONTRIBUTING.md 2>/dev/null || true
fi

# Make scripts executable
chmod +x setup.sh 2>/dev/null || true
chmod +x batch_grade.sh 2>/dev/null || true
chmod +x scripts/*.sh 2>/dev/null || true

echo "✓ Updated file permissions"

# Initial commit
echo ""
echo "Creating initial commit..."

git add .
git commit -m "Initial commit: Course Scheduler Auto-Grader v1.0

- 100% automated grading system
- Database validation
- Code analysis with AST
- Compilation testing
- Official test script execution
- Support for Part 1 and Part 2
" || echo "⚠ No changes to commit"

echo "✓ Initial commit created"

# Set up remote
echo ""
echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo ""
echo "1. Create GitHub repository:"
echo "   Go to: https://github.com/new"
echo "   Name: $PROJECT_NAME"
echo "   Description: Automated grading tool for Java Course Scheduler projects"
echo "   Public: Yes"
echo "   Don't initialize with README"
echo ""
echo "2. Connect and push:"
echo "   git remote add origin https://github.com/$GITHUB_USER/$PROJECT_NAME.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "Or use GitHub CLI:"
echo "   gh repo create $PROJECT_NAME --public --source=. --push"
echo ""
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "Project location: $PWD"
echo ""
echo "To push to GitHub, run:"
echo "  git remote add origin https://github.com/$GITHUB_USER/$PROJECT_NAME.git"
echo "  git push -u origin main"
echo ""
