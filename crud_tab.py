import tkinter as tk
from tkinter import ttk, messagebox

from db import get_connection


class CRUDTab(ttk.Frame):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.selected_pk = None
        self.fk_display_to_id = {}   # column_name -> {display_text: id}
        self.fk_id_to_display = {}   # column_name -> {id: display_text}
        self.fk_comboboxes = {}      # column_name -> the actual Combobox widget

        self._build_form()
        self._build_table()
        self.load_fk_options()
        self.refresh_table()

    # ---------------- Form ----------------
    def _build_form(self):
        frame = ttk.LabelFrame(self, text=f"{self.config.title} Details")
        frame.pack(fill="x", padx=10, pady=10)

        self.widgets = {}
        for i, col in enumerate(self.config.columns):
            row, col_pos = divmod(i, 2)
            ttk.Label(frame, text=col.label).grid(
                row=row, column=col_pos * 2, padx=5, pady=5, sticky="e"
            )
            if col.fk:
                var = tk.StringVar()
                widget = ttk.Combobox(frame, textvariable=var, width=30, state="readonly")
                self.widgets[col.name] = var
                self.fk_comboboxes[col.name] = widget
            else:
                widget = ttk.Entry(frame, width=32)
                self.widgets[col.name] = widget
            widget.grid(row=row, column=col_pos * 2 + 1, padx=5, pady=5)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10)
        ttk.Button(btn_frame, text="Add", command=self.add_record).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Update", command=self.update_record).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_record).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear_form).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_table).pack(side="left", padx=5)

    def _build_table(self):
        columns = ["pk"] + [c.name for c in self.config.columns]
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        self.tree.heading("pk", text="ID")
        self.tree.column("pk", width=0, stretch=False)
        for col in self.config.columns:
            self.tree.heading(col.name, text=col.label)
            self.tree.column(col.name, width=130)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    # ---------------- Foreign key dropdown loading ----------------
    def load_fk_options(self):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                for col in self.config.columns:
                    if not col.fk:
                        continue
                    expr = col.fk.display_expr.format(alias=col.fk.ref_table)
                    cur.execute(
                        f"SELECT {col.fk.ref_pk}, {expr} FROM {col.fk.ref_table} ORDER BY 2"
                    )
                    rows = cur.fetchall()
                    self.fk_display_to_id[col.name] = {display: str(pk) for pk, display in rows}
                    self.fk_id_to_display[col.name] = {str(pk): display for pk, display in rows}
                    self.fk_comboboxes[col.name]["values"] = list(self.fk_display_to_id[col.name].keys())
        except Exception as e:
            messagebox.showerror("Error loading dropdown options", str(e))
        finally:
            conn.close()

    # ---------------- Data operations ----------------
    def _select_query(self):
        """Builds a SELECT that joins every FK column to its human-readable value."""
        select_parts = [f"{self.config.table}.{self.config.pk_column}"]
        joins = []
        for i, col in enumerate(self.config.columns):
            if col.fk:
                alias = f"fk{i}"
                expr = col.fk.display_expr.format(alias=alias)
                select_parts.append(f"{expr} AS {col.name}")
                joins.append(
                    f"LEFT JOIN {col.fk.ref_table} {alias} "
                    f"ON {self.config.table}.{col.name} = {alias}.{col.fk.ref_pk}"
                )
            else:
                select_parts.append(f"{self.config.table}.{col.name}")
        order_col = self.config.order_by or self.config.columns[0].name
        return (
            f"SELECT {', '.join(select_parts)} FROM {self.config.table} "
            + " ".join(joins)
            + f" ORDER BY {order_col}"
        )

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(self._select_query())
                for row in cur.fetchall():
                    self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror(f"Error loading {self.config.title}", str(e))
        finally:
            conn.close()

    def _collect_values(self):
        """Read the form -> {column_name: value_for_db}. Blank optional fields
        are left out entirely so the database's own defaults/NULLs apply."""
        values = {}
        for col in self.config.columns:
            widget = self.widgets[col.name]
            raw = widget.get().strip()
            if col.fk:
                values[col.name] = self.fk_display_to_id.get(col.name, {}).get(raw)
            else:
                values[col.name] = raw if raw != "" else None
        return values

    def _validate(self, values):
        for col in self.config.columns:
            if col.required and not values.get(col.name):
                messagebox.showwarning("Missing data", f"{col.label} is required.")
                return False
        return True

    @staticmethod
    def _drop_blanks(values):
        return {k: v for k, v in values.items() if v is not None}

    def add_record(self):
        values = self._collect_values()
        if not self._validate(values):
            return
        values = self._drop_blanks(values)
        cols = list(values.keys())
        placeholders = ", ".join(["%s"] * len(cols))
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO {self.config.table} ({', '.join(cols)}) "
                    f"VALUES ({placeholders})",
                    [values[c] for c in cols],
                )
            conn.commit()
            self.clear_form()
            self.refresh_table()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error adding record", str(e))
        finally:
            conn.close()

    def update_record(self):
        if not self.selected_pk:
            messagebox.showwarning("No selection", "Select a row from the table first.")
            return
        values = self._collect_values()
        if not self._validate(values):
            return
        values = self._drop_blanks(values)
        cols = list(values.keys())
        set_clause = ", ".join(f"{c}=%s" for c in cols)
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE {self.config.table} SET {set_clause} "
                    f"WHERE {self.config.pk_column}=%s",
                    [values[c] for c in cols] + [self.selected_pk],
                )
            conn.commit()
            self.clear_form()
            self.refresh_table()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error updating record", str(e))
        finally:
            conn.close()

    def delete_record(self):
        if not self.selected_pk:
            messagebox.showwarning("No selection", "Select a row from the table first.")
            return
        if not messagebox.askyesno("Confirm delete", "Delete this record?"):
            return
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"DELETE FROM {self.config.table} WHERE {self.config.pk_column}=%s",
                    (self.selected_pk,),
                )
            conn.commit()
            self.clear_form()
            self.refresh_table()
        except Exception as e:
            conn.rollback()
            messagebox.showerror(
                "Error deleting record",
                "This record may still be referenced by another table.\n" + str(e),
            )
        finally:
            conn.close()

    # ---------------- Helpers ----------------
    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.selected_pk = values[0]
        self._load_raw_record(self.selected_pk)

    def _load_raw_record(self, pk):
        """Loads the actual raw column values (not the joined display text)
        into the form, so FK dropdowns can be matched back to their id."""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                col_names = [c.name for c in self.config.columns]
                cur.execute(
                    f"SELECT {', '.join(col_names)} FROM {self.config.table} "
                    f"WHERE {self.config.pk_column}=%s",
                    (pk,),
                )
                row = cur.fetchone()
                if not row:
                    return
                for col, val in zip(self.config.columns, row):
                    widget = self.widgets[col.name]
                    if col.fk:
                        display = self.fk_id_to_display.get(col.name, {}).get(str(val), "")
                        widget.set(display)
                    else:
                        widget.delete(0, "end")
                        widget.insert(0, "" if val is None else str(val))
        except Exception as e:
            messagebox.showerror("Error loading record", str(e))
        finally:
            conn.close()

    def clear_form(self):
        for col in self.config.columns:
            widget = self.widgets[col.name]
            if col.fk:
                widget.set("")
            else:
                widget.delete(0, "end")
        self.selected_pk = None
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())