"""Handles Canvas bulk download extraction and student submission discovery."""

import zipfile
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from framework.utils import parse_canvas_filename, create_temp_dir


@dataclass
class StudentSubmission:
    student_name: str
    canvas_id: str
    submission_id: str
    zip_path: Path
    java_files: List[Path] = field(default_factory=list)
    extract_dir: Optional[Path] = None
    error: str = ""


class SubmissionHandler:
    """Discovers and extracts student submissions from Canvas downloads."""

    def __init__(self, input_path: Path):
        self.input_path = Path(input_path)
        self.temp_dir = create_temp_dir("submissions_")

    def discover_submissions(self) -> List[StudentSubmission]:
        """
        Discover student submissions from the input path.
        Handles:
        - A directory of individual student .zip files
        - A single Canvas bulk download .zip containing student zips
        - A single student .zip file
        """
        if self.input_path.is_file() and self.input_path.suffix == '.zip':
            # Could be a single student zip or a Canvas bulk download
            return self._handle_zip_file(self.input_path)
        elif self.input_path.is_dir():
            return self._handle_directory(self.input_path)
        else:
            return []

    def _handle_directory(self, directory: Path) -> List[StudentSubmission]:
        """Process a directory of individual student zip files."""
        submissions = []
        for zip_file in sorted(directory.glob("*.zip")):
            sub = self._parse_submission(zip_file)
            submissions.append(sub)
        return submissions

    def _handle_zip_file(self, zip_path: Path) -> List[StudentSubmission]:
        """Handle a single zip - either a bulk download or individual submission."""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                names = zf.namelist()
                # Check if it's a bulk download (contains .zip files)
                inner_zips = [n for n in names if n.endswith('.zip')]
                if inner_zips:
                    return self._handle_bulk_download(zip_path)
                else:
                    # Single student submission
                    return [self._parse_submission(zip_path)]
        except zipfile.BadZipFile:
            sub = StudentSubmission(
                student_name=zip_path.stem,
                canvas_id="", submission_id="",
                zip_path=zip_path,
                error="Corrupt or invalid zip file"
            )
            return [sub]

    def _handle_bulk_download(self, bulk_zip: Path) -> List[StudentSubmission]:
        """Extract a Canvas bulk download zip and process inner zips."""
        extract_dir = self.temp_dir / "bulk"
        extract_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(bulk_zip, 'r') as zf:
            zf.extractall(extract_dir)

        return self._handle_directory(extract_dir)

    def _parse_submission(self, zip_path: Path) -> StudentSubmission:
        """Parse a single student submission zip."""
        info = parse_canvas_filename(zip_path.name)
        sub = StudentSubmission(
            student_name=info["student_name"],
            canvas_id=info["canvas_id"],
            submission_id=info["submission_id"],
            zip_path=zip_path
        )
        return sub

    def extract_java_files(self, submission: StudentSubmission,
                           require_project_structure: bool = True) -> List[Path]:
        """
        Extract Java files from a student's zip.
        If require_project_structure is True, the zip must contain a project
        folder with a src/ directory (NetBeans format). Raw .java files at
        the zip root are rejected.
        Returns list of paths to extracted .java files.
        """
        extract_dir = self.temp_dir / f"student_{submission.canvas_id or submission.student_name}"
        extract_dir.mkdir(parents=True, exist_ok=True)
        submission.extract_dir = extract_dir

        try:
            with zipfile.ZipFile(submission.zip_path, 'r') as zf:
                zf.extractall(extract_dir)
        except zipfile.BadZipFile:
            submission.error = "Corrupt or invalid zip file"
            return []
        except Exception as e:
            submission.error = f"Extraction error: {e}"
            return []

        # Find all .java files, excluding macOS resource forks and __MACOSX dirs
        java_files = [
            f for f in extract_dir.rglob("*.java")
            if '__MACOSX' not in f.parts and not f.name.startswith('._')
        ]

        if not java_files:
            submission.error = "No .java files found in submission"
            return []

        # Check for proper project structure (must have src/ directory)
        src_files = [f for f in java_files if 'src' in f.parts]

        if require_project_structure and not src_files:
            submission.error = (
                "Improper submission format: no project structure found. "
                "Expected a zipped NetBeans project folder containing a src/ directory. "
                "Student submitted raw .java file(s) without project structure."
            )
            return []

        if src_files:
            java_files = src_files

        submission.java_files = java_files
        return java_files

    def cleanup(self):
        """Remove all temporary files."""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
