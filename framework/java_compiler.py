"""Java compilation and execution utilities."""

import os
import re
import subprocess
import shutil
from pathlib import Path
from typing import List, Union


class JavaCompiler:
    """Compiles and runs Java source files, capturing output."""

    def __init__(self, java_files: Union[Path, List[Path]], work_dir: Path):
        if isinstance(java_files, Path):
            java_files = [java_files]
        self.java_files = java_files
        self.work_dir = work_dir
        self.build_dir = work_dir / "build"
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self._file_info = []
        self._analyze_files()

    def _analyze_files(self):
        for f in self.java_files:
            source = f.read_text(errors='ignore')
            pkg = self._detect_package(source)
            cls = self._detect_class_name(source, f)
            has_main = bool(re.search(r'public\s+static\s+void\s+main', source))
            self._file_info.append({
                'file': f, 'package': pkg, 'class_name': cls,
                'has_main': has_main
            })

    @staticmethod
    def _detect_package(source: str) -> str:
        match = re.search(r'package\s+([\w.]+)\s*;', source)
        return match.group(1) if match else ""

    @staticmethod
    def _detect_class_name(source: str, java_file: Path) -> str:
        match = re.search(r'public\s+class\s+(\w+)', source)
        return match.group(1) if match else java_file.stem

    @property
    def main_class_fqn(self) -> str:
        """Fully qualified name of the class with main()."""
        for info in self._file_info:
            if info['has_main']:
                if info['package']:
                    return f"{info['package']}.{info['class_name']}"
                return info['class_name']
        # Fallback to first file
        info = self._file_info[0]
        if info['package']:
            return f"{info['package']}.{info['class_name']}"
        return info['class_name']

    def compile(self, timeout: int = 30) -> tuple:
        """
        Compile all Java files. Sets up package directory structure if needed.
        Returns (success: bool, error_output: str).
        """
        src_root = self.work_dir / "src"
        src_root.mkdir(parents=True, exist_ok=True)

        target_files = []
        for info in self._file_info:
            if info['package']:
                pkg_dir = src_root / info['package'].replace('.', os.sep)
                pkg_dir.mkdir(parents=True, exist_ok=True)
                target = pkg_dir / info['file'].name
            else:
                target = src_root / info['file'].name
            shutil.copy2(info['file'], target)
            target_files.append(target)

        cmd = ["javac", "-d", str(self.build_dir), "-sourcepath", str(src_root)]
        cmd.extend(str(t) for t in target_files)

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
        Run the compiled main class and capture stdout.
        Returns (success: bool, stdout_output: str).
        """
        cmd = [
            "java",
            "-cp", str(self.build_dir),
            self.main_class_fqn
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
