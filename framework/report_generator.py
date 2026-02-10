"""HTML report generator for grading results."""

import html
from datetime import datetime
from pathlib import Path
from typing import List

from framework.rubric import GradingResult


class HTMLReportGenerator:
    """Generates a single self-contained HTML report for a batch of graded submissions."""

    def __init__(self, assignment_name: str, results: List[GradingResult]):
        self.assignment_name = assignment_name
        self.results = sorted(results, key=lambda r: r.student_name.lower())

    def generate(self, output_path: Path) -> Path:
        """Generate the HTML report file."""
        html_content = self._build_html()
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content, encoding='utf-8')
        return output_path

    def _build_html(self) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        count = len(self.results)
        avg_score = sum(r.total_score for r in self.results) / count if count else 0

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{self.assignment_name} - Grading Report</title>
<style>
{self._css()}
</style>
</head>
<body>
<div class="container">
    <h1>{self.assignment_name} - Grading Report</h1>
    <div class="meta">
        Generated: {timestamp} &bull; Students: {count} &bull; Average: {avg_score:.1f}/100
    </div>

    <h2>Summary</h2>
    {self._summary_table()}

    <h2>Detailed Results</h2>
    {self._detail_sections()}
</div>
<script>
{self._js()}
</script>
</body>
</html>"""

    def _css(self) -> str:
        return """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }
.container { max-width: 1200px; margin: 0 auto; padding: 20px; }
h1 { margin-bottom: 5px; color: #2c3e50; }
h2 { margin: 25px 0 10px; color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }
.meta { color: #7f8c8d; margin-bottom: 20px; font-size: 0.9em; }

/* Summary Table */
.summary-table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.summary-table th { background: #2c3e50; color: white; padding: 10px 12px; text-align: left; font-size: 0.85em; }
.summary-table td { padding: 8px 12px; border-bottom: 1px solid #ecf0f1; font-size: 0.9em; }
.summary-table tr:hover { background: #f8f9fa; }
.score-high { }
.score-high td:nth-child(2) { color: #27ae60; font-weight: bold; }
.score-mid td:nth-child(2) { color: #f39c12; font-weight: bold; }
.score-low td:nth-child(2) { color: #e74c3c; font-weight: bold; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
.badge-pass { background: #d4edda; color: #155724; }
.badge-fail { background: #f8d7da; color: #721c24; }
.badge-grade { background: #2c3e50; color: white; }

/* Detail Sections */
details { background: white; margin: 10px 0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden; }
summary { padding: 12px 16px; cursor: pointer; font-weight: 600; font-size: 1em; display: flex; align-items: center; gap: 10px; }
summary:hover { background: #f8f9fa; }
.detail-content { padding: 0 16px 16px; }

/* Rubric Table */
.rubric-table { width: 100%; border-collapse: collapse; margin: 10px 0; }
.rubric-table th { background: #ecf0f1; padding: 8px; text-align: left; font-size: 0.85em; }
.rubric-table td { padding: 8px; border-bottom: 1px solid #ecf0f1; font-size: 0.9em; }
.rubric-pass { background: #f0fff0; }
.rubric-fail { background: #fff5f5; }
.deduction { color: #e74c3c; font-weight: bold; }
.no-deduction { color: #27ae60; }
.category-header { background: #f8f9fa; font-weight: bold; }

/* Code/Output */
pre { background: #2d2d2d; color: #f8f8f2; padding: 12px; border-radius: 6px; overflow-x: auto; font-size: 0.85em; line-height: 1.4; margin: 8px 0; max-height: 400px; overflow-y: auto; }
.section-label { font-weight: 600; margin: 12px 0 4px; color: #2c3e50; font-size: 0.95em; }
.compiler-error { background: #1e1e1e; color: #f44747; }
.output-box { background: #1e3a1e; color: #98fb98; }
.expected-box { background: #1e1e3a; color: #87ceeb; }

/* Buttons */
.btn { padding: 6px 14px; border: none; border-radius: 4px; cursor: pointer; font-size: 0.85em; margin: 4px; }
.btn-expand { background: #3498db; color: white; }
.btn-expand:hover { background: #2980b9; }
"""

    def _js(self) -> str:
        return """
function expandAll() {
    document.querySelectorAll('details').forEach(d => d.open = true);
}
function collapseAll() {
    document.querySelectorAll('details').forEach(d => d.open = false);
}
"""

    def _summary_table(self) -> str:
        rows = []
        for r in self.results:
            score_class = "score-high" if r.total_score >= 90 else ("score-mid" if r.total_score >= 70 else "score-low")
            compile_badge = '<span class="badge badge-pass">Yes</span>' if r.compilation_success else '<span class="badge badge-fail">No</span>'
            run_badge = '<span class="badge badge-pass">Yes</span>' if r.execution_success else '<span class="badge badge-fail">No</span>'

            rows.append(f"""<tr class="{score_class}">
    <td>{html.escape(r.student_name)}</td>
    <td>{r.total_score}/{r.max_score}</td>
    <td><span class="badge badge-grade">{r.letter_grade}</span></td>
    <td>{'-' + str(r.class_deductions) if r.class_deductions else '0'}</td>
    <td>{'-' + str(r.main_deductions) if r.main_deductions else '0'}</td>
    <td>{'-' + str(min(len(r.oop_notes)*2, 15)) if r.oop_notes else '0'}</td>
    <td>{compile_badge}</td>
    <td>{run_badge}</td>
</tr>""")

        return f"""<table class="summary-table">
<tr>
    <th>Student</th>
    <th>Score</th>
    <th>Grade</th>
    <th>Class Deductions</th>
    <th>Main Deductions</th>
    <th>OOP Deductions</th>
    <th>Compiles</th>
    <th>Runs</th>
</tr>
{''.join(rows)}
</table>
<div style="margin-top:10px;">
    <button class="btn btn-expand" onclick="expandAll()">Expand All</button>
    <button class="btn btn-expand" onclick="collapseAll()">Collapse All</button>
</div>"""

    def _detail_sections(self) -> str:
        sections = []
        for r in self.results:
            sections.append(self._student_detail(r))
        return '\n'.join(sections)

    def _student_detail(self, r: GradingResult) -> str:
        # Score indicator
        indicator = "&#9989;" if r.total_score >= 90 else ("&#9888;&#65039;" if r.total_score >= 70 else "&#10060;")

        # Rubric table
        rubric_rows = []
        current_category = ""
        for item in r.rubric_items:
            if item.category != current_category:
                current_category = item.category
                rubric_rows.append(f'<tr class="category-header"><td colspan="4">{html.escape(current_category)}</td></tr>')

            row_class = "rubric-pass" if item.passed else "rubric-fail"
            deduction_str = f'<span class="deduction">-{item.deduction}</span>' if item.deduction > 0 else '<span class="no-deduction">0</span>'

            rubric_rows.append(f"""<tr class="{row_class}">
    <td>{html.escape(item.description)}</td>
    <td>-{item.max_deduction}</td>
    <td>{deduction_str}</td>
    <td>{html.escape(item.notes)}</td>
</tr>""")

        # OOP notes
        oop_html = ""
        if r.oop_notes:
            oop_items = ''.join(f'<li>{html.escape(n)}</li>' for n in r.oop_notes)
            oop_deduction = min(len(r.oop_notes) * 2, 15)
            oop_html = f"""<div class="section-label">OOP Practice Issues (deduction: -{oop_deduction}, capped at -15)</div>
<ul>{oop_items}</ul>"""

        # Compiler output
        compiler_html = ""
        if r.compiler_errors:
            compiler_html = f"""<div class="section-label">Compiler Output</div>
<pre class="compiler-error">{html.escape(r.compiler_errors)}</pre>"""

        # Expected output
        expected_html = ""
        if r.expected_output:
            expected_html = f"""<div class="section-label">Expected Output</div>
<pre class="expected-box">{html.escape(r.expected_output)}</pre>"""

        # Program output
        output_html = ""
        if r.actual_output:
            output_html = f"""<div class="section-label">Program Output</div>
<pre class="output-box">{html.escape(r.actual_output)}</pre>"""
        elif r.error_message:
            output_html = f"""<div class="section-label">Error</div>
<pre class="compiler-error">{html.escape(r.error_message)}</pre>"""

        return f"""<details>
<summary>{indicator} {html.escape(r.student_name)} - {r.total_score}/{r.max_score} ({r.letter_grade})</summary>
<div class="detail-content">
    <table class="rubric-table">
    <tr><th>Rubric Item</th><th>Max Deduction</th><th>Actual</th><th>Notes</th></tr>
    {''.join(rubric_rows)}
    </table>
    {oop_html}
    {compiler_html}
    {expected_html}
    {output_html}
    <div class="section-label">Source Code</div>
    <pre>{html.escape(r.source_code)}</pre>
</div>
</details>"""
