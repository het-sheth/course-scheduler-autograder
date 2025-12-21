#!/usr/bin/env python3
"""
GUI Interface for Course Scheduler Auto-Grader
Provides a simple interface for grading submissions
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading
import os
from pathlib import Path
from course_scheduler_autograder import CourseSchedulerGrader
from batch_grader import BatchGrader

class AutoGraderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Course Scheduler Auto-Grader")
        self.root.geometry("800x600")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.single_tab = ttk.Frame(self.notebook)
        self.batch_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.single_tab, text="Single Submission")
        self.notebook.add(self.batch_tab, text="Batch Grading")
        
        # Setup tabs
        self.setup_single_tab()
        self.setup_batch_tab()
    
    def setup_single_tab(self):
        """Setup single submission grading tab"""
        frame = ttk.Frame(self.single_tab, padding="10")
        frame.pack(fill='both', expand=True)
        
        # Project selection
        ttk.Label(frame, text="Project ZIP:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky='w', pady=5
        )
        self.project_path = tk.StringVar()
        ttk.Entry(frame, textvariable=self.project_path, width=50).grid(
            row=0, column=1, padx=5, pady=5
        )
        ttk.Button(frame, text="Browse...", command=self.browse_project).grid(
            row=0, column=2, padx=5, pady=5
        )
        
        # Database selection
        ttk.Label(frame, text="Database ZIP:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky='w', pady=5
        )
        self.database_path = tk.StringVar()
        ttk.Entry(frame, textvariable=self.database_path, width=50).grid(
            row=1, column=1, padx=5, pady=5
        )
        ttk.Button(frame, text="Browse...", command=self.browse_database).grid(
            row=1, column=2, padx=5, pady=5
        )
        
        # Part selection
        ttk.Label(frame, text="Project Part:", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky='w', pady=5
        )
        self.part = tk.IntVar(value=1)
        ttk.Radiobutton(frame, text="Part 1", variable=self.part, value=1).grid(
            row=2, column=1, sticky='w', padx=5
        )
        ttk.Radiobutton(frame, text="Part 2", variable=self.part, value=2).grid(
            row=2, column=1, sticky='e', padx=5
        )
        
        # Grade button
        ttk.Button(
            frame, 
            text="Grade Submission", 
            command=self.grade_single,
            style='Accent.TButton'
        ).grid(row=3, column=1, pady=20)
        
        # Output area
        ttk.Label(frame, text="Grading Output:", font=('Arial', 10, 'bold')).grid(
            row=4, column=0, sticky='nw', pady=5
        )
        self.single_output = scrolledtext.ScrolledText(
            frame, 
            height=20, 
            width=70,
            font=('Courier', 9)
        )
        self.single_output.grid(row=5, column=0, columnspan=3, pady=5)
    
    def setup_batch_tab(self):
        """Setup batch grading tab"""
        frame = ttk.Frame(self.batch_tab, padding="10")
        frame.pack(fill='both', expand=True)
        
        # Submissions directory
        ttk.Label(frame, text="Submissions Directory:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky='w', pady=5
        )
        self.submissions_dir = tk.StringVar()
        ttk.Entry(frame, textvariable=self.submissions_dir, width=50).grid(
            row=0, column=1, padx=5, pady=5
        )
        ttk.Button(frame, text="Browse...", command=self.browse_submissions).grid(
            row=0, column=2, padx=5, pady=5
        )
        
        # Output directory
        ttk.Label(frame, text="Output Directory:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky='w', pady=5
        )
        self.output_dir = tk.StringVar()
        ttk.Entry(frame, textvariable=self.output_dir, width=50).grid(
            row=1, column=1, padx=5, pady=5
        )
        ttk.Button(frame, text="Browse...", command=self.browse_output).grid(
            row=1, column=2, padx=5, pady=5
        )
        
        # Part selection
        ttk.Label(frame, text="Project Part:", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky='w', pady=5
        )
        self.batch_part = tk.IntVar(value=1)
        ttk.Radiobutton(frame, text="Part 1", variable=self.batch_part, value=1).grid(
            row=2, column=1, sticky='w', padx=5
        )
        ttk.Radiobutton(frame, text="Part 2", variable=self.batch_part, value=2).grid(
            row=2, column=1, sticky='e', padx=5
        )
        
        # Grade button
        ttk.Button(
            frame, 
            text="Grade All Submissions", 
            command=self.grade_batch,
            style='Accent.TButton'
        ).grid(row=3, column=1, pady=20)
        
        # Progress bar
        ttk.Label(frame, text="Progress:", font=('Arial', 10, 'bold')).grid(
            row=4, column=0, sticky='w', pady=5
        )
        self.progress = ttk.Progressbar(frame, length=400, mode='indeterminate')
        self.progress.grid(row=4, column=1, columnspan=2, pady=5)
        
        # Output area
        ttk.Label(frame, text="Grading Output:", font=('Arial', 10, 'bold')).grid(
            row=5, column=0, sticky='nw', pady=5
        )
        self.batch_output = scrolledtext.ScrolledText(
            frame, 
            height=15, 
            width=70,
            font=('Courier', 9)
        )
        self.batch_output.grid(row=6, column=0, columnspan=3, pady=5)
    
    def browse_project(self):
        """Browse for project ZIP file"""
        filename = filedialog.askopenfilename(
            title="Select Project ZIP",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )
        if filename:
            self.project_path.set(filename)
    
    def browse_database(self):
        """Browse for database ZIP file"""
        filename = filedialog.askopenfilename(
            title="Select Database ZIP",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )
        if filename:
            self.database_path.set(filename)
    
    def browse_submissions(self):
        """Browse for submissions directory"""
        dirname = filedialog.askdirectory(title="Select Submissions Directory")
        if dirname:
            self.submissions_dir.set(dirname)
    
    def browse_output(self):
        """Browse for output directory"""
        dirname = filedialog.askdirectory(title="Select Output Directory")
        if dirname:
            self.output_dir.set(dirname)
    
    def grade_single(self):
        """Grade single submission"""
        project = self.project_path.get()
        database = self.database_path.get()
        part = self.part.get()
        
        if not project or not database:
            messagebox.showerror("Error", "Please select both project and database files")
            return
        
        if not os.path.exists(project):
            messagebox.showerror("Error", f"Project file not found: {project}")
            return
        
        if not os.path.exists(database):
            messagebox.showerror("Error", f"Database file not found: {database}")
            return
        
        # Clear output
        self.single_output.delete(1.0, tk.END)
        self.single_output.insert(tk.END, "Starting grading...\n\n")
        
        # Run grading in separate thread
        def grade():
            try:
                # Redirect output to text widget
                import sys
                from io import StringIO
                
                old_stdout = sys.stdout
                sys.stdout = StringIO()
                
                grader = CourseSchedulerGrader(project, database, part)
                report_file = grader.grade()
                
                output = sys.stdout.getvalue()
                sys.stdout = old_stdout
                
                self.single_output.insert(tk.END, output)
                
                if report_file:
                    self.single_output.insert(tk.END, f"\n\n✓ Grading complete!\n")
                    self.single_output.insert(tk.END, f"Report saved to: {report_file}\n")
                    messagebox.showinfo("Success", "Grading completed successfully!")
                else:
                    self.single_output.insert(tk.END, "\n\n✗ Grading failed\n")
                    messagebox.showerror("Error", "Grading failed - check output for details")
                
            except Exception as e:
                self.single_output.insert(tk.END, f"\n\nERROR: {str(e)}\n")
                messagebox.showerror("Error", f"Grading error: {str(e)}")
        
        threading.Thread(target=grade, daemon=True).start()
    
    def grade_batch(self):
        """Grade batch submissions"""
        submissions = self.submissions_dir.get()
        output = self.output_dir.get()
        part = self.batch_part.get()
        
        if not submissions or not output:
            messagebox.showerror("Error", "Please select both submissions and output directories")
            return
        
        if not os.path.exists(submissions):
            messagebox.showerror("Error", f"Submissions directory not found: {submissions}")
            return
        
        # Create output directory if it doesn't exist
        os.makedirs(output, exist_ok=True)
        
        # Clear output
        self.batch_output.delete(1.0, tk.END)
        self.batch_output.insert(tk.END, "Starting batch grading...\n\n")
        
        # Start progress bar
        self.progress.start()
        
        # Run grading in separate thread
        def grade():
            try:
                # Redirect output to text widget
                import sys
                from io import StringIO
                
                old_stdout = sys.stdout
                sys.stdout = StringIO()
                
                grader = BatchGrader(submissions, output, part)
                grader.grade_all()
                
                batch_output = sys.stdout.getvalue()
                sys.stdout = old_stdout
                
                self.batch_output.insert(tk.END, batch_output)
                self.batch_output.insert(tk.END, f"\n\n✓ Batch grading complete!\n")
                
                self.progress.stop()
                messagebox.showinfo("Success", "Batch grading completed successfully!")
                
            except Exception as e:
                self.batch_output.insert(tk.END, f"\n\nERROR: {str(e)}\n")
                self.progress.stop()
                messagebox.showerror("Error", f"Batch grading error: {str(e)}")
        
        threading.Thread(target=grade, daemon=True).start()


def main():
    root = tk.Tk()
    app = AutoGraderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
