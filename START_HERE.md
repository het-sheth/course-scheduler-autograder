# 🚀 START HERE - GitHub Setup in 3 Steps

Welcome! You've downloaded the Course Scheduler Auto-Grader. Here's how to get it on GitHub in just **3 steps** (5 minutes).

## Quick Setup (Recommended)

### Step 1: Run the Setup Script

```bash
# Make script executable
chmod +x init_github_project.sh

# Run setup
./init_github_project.sh
```

The script will:
- Create project directory
- Initialize git
- Create directory structure
- Make initial commit
- Guide you through GitHub setup

**That's it!** Follow the on-screen instructions.

---

## Manual Setup (If you prefer)

### Step 1: Create Local Repository

```bash
# Create project folder
mkdir course-scheduler-autograder
cd course-scheduler-autograder

# Copy ALL downloaded files here
# (ultimate_autograder.py, README_GITHUB.md, etc.)

# Initialize git
git init

# Rename README_GITHUB.md to README.md
mv README_GITHUB.md README.md
```

### Step 2: Create GitHub Repository

**Option A: Via Website (Easiest)**

1. Go to https://github.com
2. Click "+" → "New repository"
3. Repository name: `course-scheduler-autograder`
4. Description: "Automated grading tool for Java Course Scheduler projects with 100% automation"
5. **Public** ✓
6. **DO NOT** check "Initialize with README" (we have our own)
7. Click "Create repository"

**Option B: Via Command Line (if you have GitHub CLI)**

```bash
gh repo create course-scheduler-autograder --public --description "Automated grading tool for Java Course Scheduler projects"
```

### Step 3: Push to GitHub

```bash
# Add all files
git add .

# Initial commit
git commit -m "Initial commit: Course Scheduler Auto-Grader v1.0"

# Connect to GitHub (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/course-scheduler-autograder.git

# Push
git branch -M main
git push -u origin main
```

**Done!** 🎉 Your project is now on GitHub!

---

## Files You Downloaded

Here's what each file does:

### Core Grading Tools
- `ultimate_autograder.py` - 100% automated grader (recommended)
- `fully_automated_grader.py` - 95% automated (static analysis)
- `course_scheduler_autograder.py` - 65% automated (database only)
- `test_script_executor.py` - Runs official test scripts
- `advanced_code_analyzer.py` - Deep code analysis
- `batch_grader.py` - Grade multiple students at once
- `autograder_gui.py` - Graphical interface

### Setup & Config
- `requirements.txt` - Python dependencies
- `setup.sh` - Installation script
- `.gitignore` - Files git should ignore

### Documentation
- `README_GITHUB.md` - Main README (rename to README.md)
- `GITHUB_SETUP.md` - Detailed GitHub instructions
- `100_PERCENT_AUTOMATED.md` - How 100% automation works
- `QUICKSTART.md` - Quick reference guide
- `CONTRIBUTING.md` - Contribution guidelines

### Other
- `LICENSE` - MIT License
- `batch_grade.sh` - Batch grading helper script
- `init_github_project.sh` - This setup script

---

## Recommended Directory Structure

Once set up, organize like this:

```
course-scheduler-autograder/
├── README.md                      # Main docs (renamed from README_GITHUB.md)
├── LICENSE
├── requirements.txt
├── setup.sh
├── .gitignore
│
├── src/ or root/                  # Python scripts
│   ├── ultimate_autograder.py
│   ├── fully_automated_grader.py
│   ├── course_scheduler_autograder.py
│   ├── test_script_executor.py
│   ├── advanced_code_analyzer.py
│   ├── batch_grader.py
│   └── autograder_gui.py
│
├── docs/                          # Documentation
│   ├── GITHUB_SETUP.md
│   ├── 100_PERCENT_AUTOMATED.md
│   ├── QUICKSTART.md
│   └── TROUBLESHOOTING.md
│
├── scripts/                       # Helper scripts
│   └── batch_grade.sh
│
└── examples/                      # Example files (optional)
    └── sample_submission/
```

---

## After Pushing to GitHub

### Customize Your Repo

1. **Update README.md**
   - Replace `YOUR_USERNAME` with your GitHub username
   - Add your name/email
   - Add any custom badges

2. **Update LICENSE**
   - Replace `[Your Name]` with your actual name
   - Change year if needed (currently 2024)

3. **Enable GitHub Features**
   - Settings → Issues ✓
   - Settings → Projects ✓
   - Settings → Wiki ✓

### Share Your Project

Add badges to README.md (optional):

```markdown
[![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/course-scheduler-autograder?style=social)](https://github.com/YOUR_USERNAME/course-scheduler-autograder)
[![GitHub forks](https://img.shields.io/github/forks/YOUR_USERNAME/course-scheduler-autograder?style=social)](https://github.com/YOUR_USERNAME/course-scheduler-autograder)
```

---

## Future Updates

When you make changes:

```bash
# Make your changes to files
# Then:

git add .
git commit -m "Description of changes"
git push
```

That's it! Changes appear on GitHub instantly.

---

## Common Issues

### Issue: "Permission denied"

```bash
# Make scripts executable
chmod +x setup.sh batch_grade.sh init_github_project.sh
```

### Issue: "Remote already exists"

```bash
# Remove existing remote
git remote remove origin

# Add correct remote
git remote add origin https://github.com/YOUR_USERNAME/course-scheduler-autograder.git
```

### Issue: "Large files won't push"

GitHub has a 100MB limit per file. If your example files are large:

```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.zip"

# Commit and push
git add .gitattributes
git commit -m "Add Git LFS"
git push
```

---

## Getting Help

- **Full setup guide**: Read `GITHUB_SETUP.md`
- **Quick reference**: Read `QUICKSTART.md`
- **How it works**: Read `100_PERCENT_AUTOMATED.md`
- **Troubleshooting**: Read `TROUBLESHOOTING.md`

---

## What's Next?

After setting up GitHub:

1. **Test it locally**
   ```bash
   pip install -r requirements.txt
   python3 ultimate_autograder.py sample.zip sample_db.zip 1
   ```

2. **Share your repo**
   - Send link to colleagues
   - Add to your resume/portfolio
   - Get feedback via GitHub Issues

3. **Keep improving**
   - Fix bugs
   - Add features
   - Update documentation

---

## Summary

**Three ways to set up:**

1. **Easiest**: Run `./init_github_project.sh` and follow prompts
2. **Simple**: Copy files, create repo on GitHub, push
3. **Detailed**: Follow `GITHUB_SETUP.md` step-by-step

**Time needed**: 5 minutes

**Result**: Professional GitHub project ready to share! 🎉

---

<div align="center">

**Choose your method above and get started!**

Questions? Check `GITHUB_SETUP.md` for detailed help.

</div>
