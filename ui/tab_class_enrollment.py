# tab_class_enrollment.py - Tab for Class Offerings, Grading Weights, and Enrollment

import tkinter as tk
from tkinter import ttk, messagebox

from models import ClassOffering, GradePercentage, GradeComponent, Enrollment
from repositories import (
    ClassRepository, SubjectRepository, TeacherRepository,
    GradePercentageRepository, GradeComponentRepository,
    GradingPeriodRepository, EnrollmentRepository, StudentRepository
)
from services import EnrollmentService, GradingService


class ClassEnrollmentTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.class_repo = ClassRepository()
        self.subject_repo = SubjectRepository()
        self.teacher_repo = TeacherRepository()
        self.percentage_repo = GradePercentageRepository()
        self.component_repo = GradeComponentRepository()
        self.period_repo = GradingPeriodRepository()
        self.enrollment_repo = EnrollmentRepository()
        self.student_repo = StudentRepository()

        self.enrollment_service = EnrollmentService(
            self.enrollment_repo, self.student_repo, self.class_repo
        )
        self.grading_service = GradingService(
            self.enrollment_repo, self.percentage_repo, self.component_repo
        )

        self.selected_offering_id = None
        self.subject_map = {}
        self.teacher_map = {}
        self.student_map = {}

        self._build_ui()
        self.refresh_all()

    def _build_ui(self):
        # 1. Class offerings form and table
        top_frame = ttk.LabelFrame(self, text="1. Class Offerings")
        top_frame.pack(fill="x", padx=10, pady=5)

        form = ttk.Frame(top_frame)
        form.pack(fill="x", padx=5, pady=5)

        ttk.Label(form, text="Class Code:").grid(row=0, column=0, padx=4, pady=3, sticky="e")
        self.entry_code = ttk.Entry(form, width=18)
        self.entry_code.grid(row=0, column=1, padx=4, pady=3, sticky="w")

        ttk.Label(form, text="Subject:").grid(row=0, column=2, padx=4, pady=3, sticky="e")
        self.cb_subject = ttk.Combobox(form, width=28, state="readonly")
        self.cb_subject.grid(row=0, column=3, padx=4, pady=3, sticky="w")

        ttk.Label(form, text="Teacher:").grid(row=0, column=4, padx=4, pady=3, sticky="e")
        self.cb_teacher = ttk.Combobox(form, width=24, state="readonly")
        self.cb_teacher.grid(row=0, column=5, padx=4, pady=3, sticky="w")

        ttk.Label(form, text="Section:").grid(row=1, column=0, padx=4, pady=3, sticky="e")
        self.entry_section = ttk.Entry(form, width=18)
        self.entry_section.grid(row=1, column=1, padx=4, pady=3, sticky="w")

        ttk.Label(form, text="Schedule:").grid(row=1, column=2, padx=4, pady=3, sticky="e")
        self.entry_schedule = ttk.Entry(form, width=28)
        self.entry_schedule.grid(row=1, column=3, padx=4, pady=3, sticky="w")

        ttk.Label(form, text="Room:").grid(row=1, column=4, padx=4, pady=3, sticky="e")
        self.entry_room = ttk.Entry(form, width=24)
        self.entry_room.grid(row=1, column=5, padx=4, pady=3, sticky="w")

        ttk.Label(form, text="School Year:").grid(row=2, column=0, padx=4, pady=3, sticky="e")
        self.entry_sy = ttk.Entry(form, width=18)
        self.entry_sy.insert(0, "2026-2027")
        self.entry_sy.grid(row=2, column=1, padx=4, pady=3, sticky="w")

        ttk.Label(form, text="Semester:").grid(row=2, column=2, padx=4, pady=3, sticky="e")
        self.cb_semester = ttk.Combobox(form, values=["1st Semester", "2nd Semester", "Summer"], width=26, state="readonly")
        self.cb_semester.set("1st Semester")
        self.cb_semester.grid(row=2, column=3, padx=4, pady=3, sticky="w")

        btn_bar = ttk.Frame(top_frame)
        btn_bar.pack(fill="x", padx=5, pady=4)
        ttk.Button(btn_bar, text="Add Class", command=self.add_class).pack(side="left", padx=4)
        ttk.Button(btn_bar, text="Update Class", command=self.update_class).pack(side="left", padx=4)
        ttk.Button(btn_bar, text="Delete Class", command=self.delete_class).pack(side="left", padx=4)
        ttk.Button(btn_bar, text="Clear", command=self.clear_class_form).pack(side="left", padx=4)
        ttk.Button(btn_bar, text="Refresh All", command=self.refresh_all).pack(side="left", padx=4)

        # classes table
        cols = ("id", "code", "subject", "teacher", "section", "schedule", "room", "term")
        self.tree_classes = ttk.Treeview(top_frame, columns=cols, show="headings", height=5)
        self.tree_classes.heading("id", text="ID")
        self.tree_classes.heading("code", text="Class Code")
        self.tree_classes.heading("subject", text="Subject")
        self.tree_classes.heading("teacher", text="Teacher")
        self.tree_classes.heading("section", text="Section")
        self.tree_classes.heading("schedule", text="Schedule")
        self.tree_classes.heading("room", text="Room")
        self.tree_classes.heading("term", text="Term / SY")

        self.tree_classes.column("id", width=0, stretch=False)
        self.tree_classes.column("code", width=100)
        self.tree_classes.column("subject", width=160)
        self.tree_classes.column("teacher", width=140)
        self.tree_classes.column("section", width=90)
        self.tree_classes.column("schedule", width=130)
        self.tree_classes.column("room", width=90)
        self.tree_classes.column("term", width=130)
        self.tree_classes.pack(fill="x", padx=5, pady=5)
        self.tree_classes.bind("<<TreeviewSelect>>", self.on_class_select)

        # bottom split: weights & components on left, student enrollments on right
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 2. Grading Weights & Components
        left_frame = ttk.LabelFrame(bottom_frame, text="2. Grading Weights & Components (for selected class)")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        w_ctrl = ttk.Frame(left_frame)
        w_ctrl.pack(fill="x", padx=5, pady=3)
        ttk.Label(w_ctrl, text="Type:").pack(side="left", padx=2)
        self.cb_weight_type = ttk.Combobox(w_ctrl, values=["Quiz", "Laboratory", "Exam", "Project", "Assignment"], width=12)
        self.cb_weight_type.set("Quiz")
        self.cb_weight_type.pack(side="left", padx=2)

        ttk.Label(w_ctrl, text="Weight %:").pack(side="left", padx=2)
        self.entry_weight_val = ttk.Entry(w_ctrl, width=6)
        self.entry_weight_val.pack(side="left", padx=2)
        ttk.Button(w_ctrl, text="Set Weight", command=self.save_weight).pack(side="left", padx=3)
        ttk.Button(w_ctrl, text="Delete Weight", command=self.delete_weight).pack(side="left", padx=3)

        self.lbl_weight_total = ttk.Label(left_frame, text="Total Weight: 0.0%", font=("Segoe UI", 9, "bold"))
        self.lbl_weight_total.pack(anchor="w", padx=8, pady=2)

        cols_w = ("id", "type", "percent")
        self.tree_weights = ttk.Treeview(left_frame, columns=cols_w, show="headings", height=4)
        self.tree_weights.heading("id", text="ID")
        self.tree_weights.heading("type", text="Category")
        self.tree_weights.heading("percent", text="Percentage (%)")
        self.tree_weights.column("id", width=0, stretch=False)
        self.tree_weights.column("type", width=140)
        self.tree_weights.column("percent", width=90)
        self.tree_weights.pack(fill="x", padx=5, pady=3)

        # add component box
        comp_box = ttk.LabelFrame(left_frame, text="Add Assessable Component")
        comp_box.pack(fill="x", padx=5, pady=5)
        c_row1 = ttk.Frame(comp_box)
        c_row1.pack(fill="x", padx=4, pady=2)
        ttk.Label(c_row1, text="Period:").pack(side="left", padx=2)
        self.cb_period = ttk.Combobox(c_row1, width=10, state="readonly")
        self.cb_period.pack(side="left", padx=2)
        ttk.Label(c_row1, text="Category:").pack(side="left", padx=2)
        self.cb_comp_weight = ttk.Combobox(c_row1, width=12, state="readonly")
        self.cb_comp_weight.pack(side="left", padx=2)

        c_row2 = ttk.Frame(comp_box)
        c_row2.pack(fill="x", padx=4, pady=2)
        ttk.Label(c_row2, text="Name:").pack(side="left", padx=2)
        self.entry_comp_name = ttk.Entry(c_row2, width=14)
        self.entry_comp_name.pack(side="left", padx=2)
        ttk.Label(c_row2, text="Max Score:").pack(side="left", padx=2)
        self.entry_comp_max = ttk.Entry(c_row2, width=6)
        self.entry_comp_max.insert(0, "100")
        self.entry_comp_max.pack(side="left", padx=2)
        ttk.Button(c_row2, text="Add Component", command=self.add_component).pack(side="left", padx=4)

        cols_c = ("id", "period", "name", "type", "max_score")
        self.tree_comps = ttk.Treeview(left_frame, columns=cols_c, show="headings", height=4)
        self.tree_comps.heading("id", text="ID")
        self.tree_comps.heading("period", text="Period")
        self.tree_comps.heading("name", text="Component Name")
        self.tree_comps.heading("type", text="Category")
        self.tree_comps.heading("max_score", text="Max Score")
        self.tree_comps.column("id", width=0, stretch=False)
        self.tree_comps.column("period", width=70)
        self.tree_comps.column("name", width=120)
        self.tree_comps.column("type", width=80)
        self.tree_comps.column("max_score", width=70)
        self.tree_comps.pack(fill="both", expand=True, padx=5, pady=3)

        # 3. Class Enrollment
        right_frame = ttk.LabelFrame(bottom_frame, text="3. Student Enrollment (for selected class)")
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        en_ctrl = ttk.Frame(right_frame)
        en_ctrl.pack(fill="x", padx=5, pady=4)
        ttk.Label(en_ctrl, text="Select Student:").pack(side="left", padx=3)
        self.cb_enroll_student = ttk.Combobox(en_ctrl, width=26, state="readonly")
        self.cb_enroll_student.pack(side="left", padx=3)
        ttk.Button(en_ctrl, text="Enroll Student", command=self.enroll_student).pack(side="left", padx=3)
        ttk.Button(en_ctrl, text="Drop Selected", command=self.drop_student).pack(side="left", padx=3)
        ttk.Button(en_ctrl, text="Remove", command=self.remove_enrollment).pack(side="left", padx=3)

        cols_e = ("id", "student_id", "student_name", "program", "enroll_date", "status")
        self.tree_enrollments = ttk.Treeview(right_frame, columns=cols_e, show="headings", height=10)
        self.tree_enrollments.heading("id", text="ID")
        self.tree_enrollments.heading("student_id", text="Student ID")
        self.tree_enrollments.heading("student_name", text="Student Name")
        self.tree_enrollments.heading("program", text="Program")
        self.tree_enrollments.heading("enroll_date", text="Enroll Date")
        self.tree_enrollments.heading("status", text="Status")

        self.tree_enrollments.column("id", width=0, stretch=False)
        self.tree_enrollments.column("student_id", width=0, stretch=False)
        self.tree_enrollments.column("student_name", width=160)
        self.tree_enrollments.column("program", width=90)
        self.tree_enrollments.column("enroll_date", width=90)
        self.tree_enrollments.column("status", width=80)
        self.tree_enrollments.pack(fill="both", expand=True, padx=5, pady=4)

    def refresh_all(self):
        self.load_dropdowns()
        self.load_classes()

    def load_dropdowns(self):
        # subjects dropdown
        subjects = self.subject_repo.find_all()
        self.subject_map = {f"{s.subject_code} - {s.subject_name}": s.subject_id for s in subjects}
        self.cb_subject["values"] = list(self.subject_map.keys())

        # teachers dropdown
        teachers = self.teacher_repo.find_all()
        self.teacher_map = {f"{t.full_name} ({t.department or 'Faculty'})": t.teacher_id for t in teachers}
        self.cb_teacher["values"] = list(self.teacher_map.keys())

        # students dropdown
        students = self.student_repo.find_all()
        self.student_map = {f"{s.full_name} - {s.email}": s.student_id for s in students}
        self.cb_enroll_student["values"] = list(self.student_map.keys())

        # grading periods
        periods = self.period_repo.find_all()
        self.period_map = {p.name: p.period_id for p in periods}
        self.cb_period["values"] = list(self.period_map.keys())
        if self.period_map:
            self.cb_period.current(0)

    def load_classes(self):
        for r in self.tree_classes.get_children():
            self.tree_classes.delete(r)
        classes = self.class_repo.find_all()
        for c in classes:
            self.tree_classes.insert("", "end", values=(
                c.offering_id, c.class_code, c.subject_name or c.subject_code,
                c.teacher_name, c.section or "", c.schedule or "", c.room or "",
                f"{c.semester} {c.school_year}"
            ))

    def on_class_select(self, event):
        sel = self.tree_classes.selection()
        if not sel:
            return
        vals = self.tree_classes.item(sel[0], "values")
        self.selected_offering_id = vals[0]
        offering = self.class_repo.find_by_id(self.selected_offering_id)
        if offering:
            self.entry_code.delete(0, "end")
            self.entry_code.insert(0, offering.class_code)
            self.entry_section.delete(0, "end")
            self.entry_section.insert(0, offering.section or "")
            self.entry_schedule.delete(0, "end")
            self.entry_schedule.insert(0, offering.schedule or "")
            self.entry_room.delete(0, "end")
            self.entry_room.insert(0, offering.room or "")
            self.entry_sy.delete(0, "end")
            self.entry_sy.insert(0, offering.school_year)
            self.cb_semester.set(offering.semester)

            for disp, sid in self.subject_map.items():
                if sid == offering.subject_id:
                    self.cb_subject.set(disp)
                    break

            for disp, tid in self.teacher_map.items():
                if tid == offering.teacher_id:
                    self.cb_teacher.set(disp)
                    break

        self.load_weights_and_components()
        self.load_enrollments()

    def clear_class_form(self):
        self.entry_code.delete(0, "end")
        self.entry_section.delete(0, "end")
        self.entry_schedule.delete(0, "end")
        self.entry_room.delete(0, "end")
        self.cb_subject.set("")
        self.cb_teacher.set("")
        self.selected_offering_id = None
        if self.tree_classes.selection():
            self.tree_classes.selection_remove(self.tree_classes.selection())

    def add_class(self):
        code = self.entry_code.get().strip()
        sub_disp = self.cb_subject.get()
        teach_disp = self.cb_teacher.get()
        sy = self.entry_sy.get().strip()
        sem = self.cb_semester.get().strip()

        if not code or not sub_disp or not teach_disp or not sy or not sem:
            messagebox.showwarning("Validation", "Class Code, Subject, Teacher, School Year, and Semester are required.")
            return

        subject_id = self.subject_map.get(sub_disp)
        teacher_id = self.teacher_map.get(teach_disp)

        offering = ClassOffering(
            class_code=code,
            subject_id=subject_id,
            teacher_id=teacher_id,
            section=self.entry_section.get().strip(),
            schedule=self.entry_schedule.get().strip(),
            room=self.entry_room.get().strip(),
            school_year=sy,
            semester=sem
        )
        try:
            saved = self.class_repo.save(offering)
            messagebox.showinfo("Success", f"Class offering {saved.class_code} created.")
            self.load_classes()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save class offering: {e}")

    def update_class(self):
        if not self.selected_offering_id:
            messagebox.showwarning("No Selection", "Please select a class to update.")
            return
        code = self.entry_code.get().strip()
        sub_disp = self.cb_subject.get()
        teach_disp = self.cb_teacher.get()
        sy = self.entry_sy.get().strip()
        sem = self.cb_semester.get().strip()

        subject_id = self.subject_map.get(sub_disp)
        teacher_id = self.teacher_map.get(teach_disp)

        offering = ClassOffering(
            offering_id=self.selected_offering_id,
            class_code=code,
            subject_id=subject_id,
            teacher_id=teacher_id,
            section=self.entry_section.get().strip(),
            schedule=self.entry_schedule.get().strip(),
            room=self.entry_room.get().strip(),
            school_year=sy,
            semester=sem
        )
        try:
            self.class_repo.save(offering)
            messagebox.showinfo("Success", f"Class offering {offering.class_code} updated.")
            self.load_classes()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update class: {e}")

    def delete_class(self):
        if not self.selected_offering_id:
            messagebox.showwarning("No Selection", "Please select a class to delete.")
            return
        if not messagebox.askyesno("Confirm Delete", "Delete this class offering? All associated components, enrollments, and grades will be removed."):
            return
        try:
            self.class_repo.delete_by_id(self.selected_offering_id)
            messagebox.showinfo("Success", "Class offering deleted.")
            self.clear_class_form()
            self.load_classes()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete class: {e}")

    # --- Weights and Components ---
    def load_weights_and_components(self):
        for r in self.tree_weights.get_children():
            self.tree_weights.delete(r)
        for r in self.tree_comps.get_children():
            self.tree_comps.delete(r)

        if not self.selected_offering_id:
            return

        percentages = self.percentage_repo.find_by_offering(self.selected_offering_id)
        total = sum(p.percentage for p in percentages)
        color = "darkgreen" if abs(total - 100.0) < 0.01 else "red"
        self.lbl_weight_total.config(
            text=f"Total Weight: {total:.1f}% {'(Valid)' if abs(total - 100.0) < 0.01 else '(Must equal 100%)'}",
            foreground=color
        )

        self.perc_dropdown_map = {}
        for p in percentages:
            self.tree_weights.insert("", "end", values=(p.percentage_id, p.component_type, f"{p.percentage:.1f}%"))
            self.perc_dropdown_map[f"{p.component_type} ({p.percentage:.0f}%)"] = p.percentage_id

        self.cb_comp_weight["values"] = list(self.perc_dropdown_map.keys())
        if self.perc_dropdown_map:
            self.cb_comp_weight.current(0)

        # components
        comps = self.component_repo.find_by_offering(self.selected_offering_id)
        for c in comps:
            self.tree_comps.insert("", "end", values=(
                c.component_id, c.period_name or "Period", c.name, c.type, f"{c.max_score:.1f}"
            ))

    def save_weight(self):
        if not self.selected_offering_id:
            messagebox.showwarning("No Class", "Select a class offering first.")
            return
        ctype = self.cb_weight_type.get().strip()
        w_val_str = self.entry_weight_val.get().strip()
        if not ctype or not w_val_str:
            messagebox.showwarning("Validation", "Enter component type and percentage weight.")
            return
        try:
            val = float(w_val_str)
            if val <= 0 or val > 100:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Validation", "Weight must be between 1 and 100.")
            return

        existing = self.percentage_repo.find_by_offering(self.selected_offering_id)
        target = None
        for p in existing:
            if p.component_type.lower() == ctype.lower():
                target = p
                break

        if target:
            target.percentage = val
            self.percentage_repo.save(target)
        else:
            self.percentage_repo.save(GradePercentage(
                offering_id=self.selected_offering_id,
                component_type=ctype,
                percentage=val
            ))

        self.load_weights_and_components()

    def delete_weight(self):
        sel = self.tree_weights.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a weight to delete.")
            return
        pid = self.tree_weights.item(sel[0], "values")[0]
        try:
            self.percentage_repo.delete_by_id(pid)
            self.load_weights_and_components()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete weight: {e}")

    def add_component(self):
        if not self.selected_offering_id:
            messagebox.showwarning("No Class", "Select a class offering first.")
            return
        p_disp = self.cb_period.get()
        w_disp = self.cb_comp_weight.get()
        name = self.entry_comp_name.get().strip()
        max_s_str = self.entry_comp_max.get().strip()

        if not p_disp or not w_disp or not name or not max_s_str:
            messagebox.showwarning("Validation", "All component fields are required.")
            return

        try:
            max_s = float(max_s_str)
            if max_s <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Validation", "Max score must be greater than 0.")
            return

        period_id = self.period_map.get(p_disp)
        percentage_id = self.perc_dropdown_map.get(w_disp)
        ctype = w_disp.split(" (")[0]

        comp = GradeComponent(
            grading_period_id=period_id,
            percentage_id=percentage_id,
            name=name,
            type=ctype,
            max_score=max_s,
            description=f"{name} task"
        )
        try:
            self.component_repo.save(comp)
            self.entry_comp_name.delete(0, "end")
            self.load_weights_and_components()
            messagebox.showinfo("Success", f"Component '{name}' added.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save component: {e}")

    # --- Enrollments ---
    def load_enrollments(self):
        for r in self.tree_enrollments.get_children():
            self.tree_enrollments.delete(r)
        if not self.selected_offering_id:
            return
        enrollments = self.enrollment_service.get_class_enrollments(self.selected_offering_id)
        for e in enrollments:
            self.tree_enrollments.insert("", "end", values=(
                e.enrollment_id, e.student_id, e.student_name,
                e.student_program or "", str(e.enroll_date or ""), e.status
            ))

    def enroll_student(self):
        if not self.selected_offering_id:
            messagebox.showwarning("No Class", "Select a class offering first.")
            return
        disp = self.cb_enroll_student.get()
        if not disp:
            messagebox.showwarning("No Student", "Select a student to enroll.")
            return
        student_id = self.student_map.get(disp)

        success, msg, _ = self.enrollment_service.enroll_student(student_id, self.selected_offering_id)
        if success:
            messagebox.showinfo("Success", msg)
            self.load_enrollments()
        else:
            messagebox.showwarning("Enrollment Issue", msg)

    def drop_student(self):
        sel = self.tree_enrollments.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select an enrolled student.")
            return
        eid = self.tree_enrollments.item(sel[0], "values")[0]
        self.enrollment_service.drop_student(eid)
        self.load_enrollments()

    def remove_enrollment(self):
        sel = self.tree_enrollments.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select an enrolled student.")
            return
        eid = self.tree_enrollments.item(sel[0], "values")[0]
        if messagebox.askyesno("Confirm Delete", "Remove student enrollment and associated scores?"):
            self.enrollment_repo.delete_by_id(eid)
            self.load_enrollments()
