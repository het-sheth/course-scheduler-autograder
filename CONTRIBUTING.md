# Contributing to Course Scheduler Auto-Grader

First off, thank you for considering contributing to this project! 🎉

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the [existing issues](https://github.com/het-sheth/course-scheduler-autograder/issues) to avoid duplicates.

**When reporting a bug, include:**
- Python version (`python3 --version`)
- Operating system
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages (full traceback)
- Sample files (if possible)

**Bug Report Template:**
```markdown
**Environment:**
- OS: Ubuntu 22.04
- Python: 3.10.5
- Derby: 10.14

**Steps to Reproduce:**
1. Run `python3 ultimate_autograder.py project.zip db.zip 1`
2. See error

**Expected:**
Grading completes successfully

**Actual:**
Error: Database connection timeout

**Error Message:**
[Paste full error here]
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- Clear description of the enhancement
- Why it would be useful
- Examples of how it would work
- Any implementation ideas

### Pull Requests

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then:
   git clone https://github.com/YOUR_USERNAME/course-scheduler-autograder.git
   cd course-scheduler-autograder
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Write clear, commented code
   - Follow the existing code style
   - Add tests if applicable
   - Update documentation

4. **Test your changes**
   ```bash
   # Run tests
   python3 -m pytest tests/
   
   # Test manually
   python3 ultimate_autograder.py sample.zip sample_db.zip 1
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add amazing feature"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**
   - Go to your fork on GitHub
   - Click "Pull Request"
   - Describe your changes
   - Link any related issues

## Code Style

### Python

Follow [PEP 8](https://pep8.org/):
- 4 spaces for indentation (no tabs)
- Line length: 100 characters max
- Use meaningful variable names
- Add docstrings to functions

**Example:**
```python
def calculate_grade(test_results: dict) -> int:
    """
    Calculate final grade from test results.
    
    Args:
        test_results: Dictionary with test scores
        
    Returns:
        Final grade as integer (0-100)
    """
    total = sum(test_results.values())
    return min(total, 100)
```

### Git Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests

**Good:**
```
Add support for Part 2 test scripts

- Implement drop student functionality
- Add waitlist reschedule logic
- Update test executor for Part 2

Fixes #42
```

**Bad:**
```
fixed stuff
```

## Testing

### Running Tests

```bash
# All tests
python3 -m pytest tests/

# Specific test
python3 -m pytest tests/test_database.py

# With coverage
python3 -m pytest --cov=src tests/
```

### Adding Tests

When adding features, include tests:

```python
def test_add_semester():
    """Test adding a semester to database"""
    executor = TestScriptExecutor(db_path, 1)
    executor.connect_database()
    executor.test_add_semester("Fall", "2025")
    # Verify semester exists
    assert semester_exists("Fall", "2025")
```

## Documentation

### Code Documentation

- Add docstrings to all functions
- Comment complex logic
- Update README if adding features

### User Documentation

Update relevant docs in `docs/`:
- `QUICKSTART.md` - For simple features
- `INSTALLATION.md` - For setup changes
- `TROUBLESHOOTING.md` - For common issues

## Project Structure

```
course-scheduler-autograder/
├── src/                    # Source code
│   ├── __init__.py
│   └── *.py               # Grader modules
├── tests/                 # Test files
│   └── test_*.py
├── docs/                  # Documentation
├── examples/              # Example files
└── scripts/               # Helper scripts
```

## Release Process

1. Update version in `__version__.py`
2. Update CHANGELOG.md
3. Create release branch
4. Tag release: `git tag -a v1.1.0 -m "Version 1.1.0"`
5. Push tags: `git push origin --tags`
6. Create GitHub release

## Questions?

Feel free to:
- Open an issue
- Start a discussion
- Contact maintainers

## Code of Conduct

Be respectful and constructive. We're all here to learn and improve education!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for making this project better! 🚀
