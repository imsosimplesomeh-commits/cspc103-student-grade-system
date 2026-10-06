# student_app.py - Standalone GUI for Student Information management

import tkinter as tk
from tkinter import ttk, messagebox

from db import init_db
from models import Student
from repositories import StudentRepository

FIELDS = ["First Name", "Last Name", "Email", "Program", "Status"]
COLUMNS = ("id", "first_name", "last_name", "email", "program", "status")


class StudentApp(tk.Tk):
    def __init__(self, repo=None):
        super().__init__()
        self.title("Student Information System - CSPC 103")
        self.geometry("860x540")
        self.selected_id = None
        self.repo = repo or StudentRepository()

        self._build_form()
        self._build_table()
        self.refresh_table()

    def _build_form(self):
        frame = ttk.LabelFrame(self, text="Student Details")
        frame.pack(fill="x", padx=10, pady=10)

        self.entries = {}
        for i, label in enumerate(FIELDS):
            ttk.Label(frame, text=label).grid(row=i // 3, column=(i % 3) * 2, padx=5, pady=5, sticky="e")
            if label == "Status":
                entry = ttk.Combobox(frame, values=["active", "inactive", "graduated", "leave"], width=23)
                entry.set("active")
            else:
                entry = ttk.Entry(frame, width=25)
            entry.grid(row=i // 3, column=(i % 3) * 2 + 1, padx=5, pady=5)
            self.entries[label] = entry

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10)
        ttk.Button(btn_frame, text="Add", command=self.add_student).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Update", command=self.update_student).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_student).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear_form).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_table).pack(side="left", padx=5)

    def _build_table(self):
        self.tree = ttk.Treeview(self, columns=COLUMNS, show="headings", height=14)
        for col in COLUMNS:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=0 if col == "id" else 140, stretch=col != "id")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            students = self.repo.find_all()
            for s in students:
                self.tree.insert("", "end", values=(
                    s.student_id, s.first_name, s.last_name, s.email, s.program or "", s.status
                ))
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load students: {e}")

    def add_student(self):
        data = self._get_form_data()
        if not data["First Name"] or not data["Last Name"] or not data["Email"]:
            messagebox.showwarning("Missing data", "First name, last name, and email are required.")
            return

        student = Student(
            first_name=data["First Name"],
            last_name=data["Last Name"],
            email=data["Email"],
            program=data["Program"],
            status=data["Status"] or "active"
        )
        try:
            self.repo.save(student)
            messagebox.showinfo("Success", f"Student {student.full_name} added successfully.")
            self.clear_form()
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error adding student", str(e))

    def update_student(self):
        if not self.selected_id:
            messagebox.showwarning("No selection", "Select a student from the table first.")
            return

        data = self._get_form_data()
        if not data["First Name"] or not data["Last Name"] or not data["Email"]:
            messagebox.showwarning("Missing data", "First name, last name, and email are required.")
            return

        student = Student(
            student_id=self.selected_id,
            first_name=data["First Name"],
            last_name=data["Last Name"],
            email=data["Email"],
            program=data["Program"],
            status=data["Status"] or "active"
        )
        try:
            self.repo.save(student)
            messagebox.showinfo("Success", f"Student {student.full_name} updated successfully.")
            self.clear_form()
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error updating student", str(e))

    def delete_student(self):
        if not self.selected_id:
            messagebox.showwarning("No selection", "Select a student from the table first.")
            return
        if not messagebox.askyesno("Confirm delete", "Are you sure you want to delete this student?"):
            return
        try:
            self.repo.delete_by_id(self.selected_id)
            messagebox.showinfo("Success", "Student removed successfully.")
            self.clear_form()
            self.refresh_table()
        except Exception as e:
            messagebox.showerror(
                "Error deleting student",
                "This student may already be enrolled in classes.\n" + str(e),
            )

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.selected_id = values[0]
        for label, val in zip(FIELDS, values[1:]):
            if label == "Status":
                self.entries[label].set(val)
            else:
                self.entries[label].delete(0, "end")
                self.entries[label].insert(0, val)

    def _get_form_data(self):
        return {label: entry.get().strip() for label, entry in self.entries.items()}

    def clear_form(self):
        for label, entry in self.entries.items():
            if label == "Status":
                entry.set("active")
            else:
                entry.delete(0, "end")
        self.selected_id = None
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())


if __name__ == "__main__":
    init_db()
    StudentApp().mainloop()
