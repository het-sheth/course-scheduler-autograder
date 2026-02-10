"""Java compilation and execution utilities."""

import os
import re
import subprocess
import shutil
from pathlib import Path


class JavaCompiler:
    """Compiles and runs a single Java source file, capturing output."""

    def __init__(self, java_file: Path, work_dir: Path):
        self.java_file = java_file
        self.work_dir = work_dir
        self.build_dir = work_dir / "build"
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.source = java_file.read_text(errors='ignore')
        self.package_name = self._detect_package()
        self.class_name = self._detect_class_name()

    def _detect_package(self) -> str:
        match = re.search(r'package\s+([\w.]+)\s*;', self.source)
        return match.group(1) if match else ""

    def _detect_class_name(self) -> str:
        match = re.search(r'public\s+class\s+(\w+)', self.source)
        return match.group(1) if match else self.java_file.stem

    @property
    def fully_qualified_name(self) -> str:
        if self.package_name:
            return f"{self.package_name}.{self.class_name}"
        return self.class_name

    def compile(self, timeout: int = 30) -> tuple:
        """
        Compile the Java file. Sets up package directory structure if needed.
        Returns (success: bool, error_output: str).
        """
        # Set up source directory with correct package structure
        src_root = self.work_dir / "src"
        src_root.mkdir(parents=True, exist_ok=True)

        if self.package_name:
            package_dir = src_root / self.package_name.replace('.', os.sep)
            package_dir.mkdir(parents=True, exist_ok=True)
            target_file = package_dir / self.java_file.name
        else:
            target_file = src_root / self.java_file.name

        shutil.copy2(self.java_file, target_file)

        cmd = [
            "javac",
            "-d", str(self.build_dir),
            "-sourcepath", str(src_root),
            str(target_file)
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            return (result.returncode == 0, result.stderr)
        except subprocess.TimeoutExpired:
            return (False, "Compilation timed out")
        except FileNotFoundError:
            return (False, "javac not found. Ensure JDK is installed and on PATH.")
        except Exception as e:
            return (False, str(e))

    def run(self, timeout: int = 10) -> tuple:
        """
        Run the compiled class and capture stdout.
        Returns (success: bool, stdout_output: str).
        """
        cmd = [
            "java",
            "-cp", str(self.build_dir),
            self.fully_qualified_name
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            if result.returncode == 0:
                return (True, result.stdout)
            else:
                return (False, f"Runtime error:\n{result.stderr}")
        except subprocess.TimeoutExpired:
            return (False, "Execution timed out (possible infinite loop)")
        except FileNotFoundError:
            return (False, "java not found. Ensure JDK is installed and on PATH.")
        except Exception as e:
            return (False, str(e))
