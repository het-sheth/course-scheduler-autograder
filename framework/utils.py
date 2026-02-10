"""Utility functions for temp directory management and path helpers."""

import tempfile
import shutil
from pathlib import Path


def create_temp_dir(prefix: str = "autograder_") -> Path:
    """Create a temporary directory for grading work."""
    temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
    return temp_dir


def cleanup_temp_dir(temp_dir: Path):
    """Remove a temporary directory and all contents."""
    if temp_dir and temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


def find_java_files(directory: Path) -> list:
    """Recursively find all .java files in a directory."""
    return list(directory.rglob("*.java"))


def parse_canvas_filename(filename: str) -> dict:
    """
    Parse a Canvas bulk download filename.
    Format: studentname_canvasID_submissionID_ProjectName.zip
    Returns dict with student_name, canvas_id, submission_id, project_name.
    """
    stem = Path(filename).stem
    parts = stem.split('_')

    # Find the first all-digit segment (that's the canvas ID)
    for i, part in enumerate(parts):
        if part.isdigit() and i + 1 < len(parts) and parts[i + 1].isdigit():
            return {
                "student_name": '_'.join(parts[:i]),
                "canvas_id": parts[i],
                "submission_id": parts[i + 1],
                "project_name": '_'.join(parts[i + 2:])
            }

    # Fallback: treat entire stem as student name
    return {
        "student_name": stem,
        "canvas_id": "",
        "submission_id": "",
        "project_name": ""
    }
