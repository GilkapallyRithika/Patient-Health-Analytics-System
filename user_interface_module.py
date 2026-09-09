"""
user_interface_module.py
Tkinter-based GUI for the Patient Health Analytics System.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

from load_dataset_module import load_patient_data
from statistics_module import FeatureStatistics
from query_module import QueryEngine


# ──────────────────────────────────────────────────────────────────────────────
# Helper to locate the dataset relative to this file
# ──────────────────────────────────────────────────────────────────────────────
DATASET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.csv")

NUMERIC_FEATURES = [
    "Age", "Average Glucose Level", "BMI", "Sleep Hours", "Stroke Risk Score"
]

QUERY_LABELS = [
    "Q1  – Smokers / Formerly smoked with Hypertension (age stats)",
    "Q2  – Heart Disease patients (age & glucose stats)",
    "Q3  – Gender × Hypertension × Stroke (age stats)",
    "Q4  – Physical Activity levels (BMI, glucose, risk score)",
    "Q5  – Urban vs Rural stroke patients (age stats)",
    "Q6  – Dietary habits: stroke vs no stroke",
    "Q7  – Hypertension = 1 AND Stroke = 1 (patient list)",
    "Q8  – Heart Disease AND Stroke (patient list)",
    "Q9  – Average sleep hours: stroke vs no stroke",
    "Q10 – Flexible patient filter (age, gender, smoking, region)",
    "Q11 – Risk group categorisation (Low / Medium / High)",
    "Q12 – Regional health summary (North / South / East / West)",
]


class HealthAnalyticsApp(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("Patient Health Analytics System")
        self.geometry("980x700")
        self.resizable(True, True)
        self.configure(bg="#f0f4f8")

        self.patient_data = []
        self.engine = None
        self.feat_stats = None

        self._build_ui()
        self._load_data()

    # ──────────────────────────────────── UI construction ────────────────────
    def _build_ui(self):
        # ── top bar ──────────────────────────────────────────────────────────
        top = tk.Frame(self, bg="#1a3c5e", pady=8)
        top.pack(fill="x")
        tk.Label(top, text="Patient Health Analytics System",
                 font=("Helvetica", 16, "bold"), fg="white", bg="#1a3c5e"
                 ).pack()

        # ── main frame ───────────────────────────────────────────────────────
        main = tk.Frame(self, bg="#f0f4f8")
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # left panel – query selector + stats selector
        left = tk.Frame(main, bg="#f0f4f8", width=300)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)

        self._build_left_panel(left)

        # right panel – results
        right = tk.Frame(main, bg="#f0f4f8")
        right.pack(side="left", fill="both", expand=True)
        self._build_right_panel(right)

    def _build_left_panel(self, parent):
        # ── query list ───────────────────────────────────────────────────────
        tk.Label(parent, text="Select Query", font=("Helvetica", 11, "bold"),
                 bg="#f0f4f8", fg="#2c3e50").pack(anchor="w")

        list_frame = tk.Frame(parent, bg="#f0f4f8")
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.query_listbox = tk.Listbox(
            list_frame, yscrollcommand=scrollbar.set,
            font=("Helvetica", 9), selectbackground="#1a3c5e",
            selectforeground="white", activestyle="none",
            bg="white", fg="#2c3e50",
            height=12
        )
        for label in QUERY_LABELS:
            self.query_listbox.insert("end", label)
        self.query_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.query_listbox.yview)

        # ── Q10 filter inputs ────────────────────────────────────────────────
        filter_frame = tk.LabelFrame(parent, text="Q10 Filters (optional)",
                                     bg="#f0f4f8", fg="#2c3e50", font=("Helvetica", 9))
        filter_frame.pack(fill="x", pady=(6, 0))

        def lbl_entry(frame, text, row):
            tk.Label(frame, text=text, bg="#f0f4f8", fg="#2c3e50",
                     font=("Helvetica", 9)).grid(row=row, column=0, sticky="w", padx=4)
            entry = tk.Entry(frame, width=14, font=("Helvetica", 9),
                             bg="white", fg="#2c3e50", insertbackground="#2c3e50")
            entry.grid(row=row, column=1, sticky="w", padx=4, pady=2)
            return entry

        self.e_age_min  = lbl_entry(filter_frame, "Age min:",       0)
        self.e_age_max  = lbl_entry(filter_frame, "Age max:",       1)
        self.e_gender   = lbl_entry(filter_frame, "Gender:",        2)
        self.e_smoking  = lbl_entry(filter_frame, "Smoking status:", 3)
        self.e_region   = lbl_entry(filter_frame, "Region:",        4)

        # ── stats feature dropdown ───────────────────────────────────────────
        stats_frame = tk.LabelFrame(parent, text="Descriptive Statistics",
                                    bg="#f0f4f8", fg="#2c3e50", font=("Helvetica", 9))
        stats_frame.pack(fill="x", pady=(6, 0))

        self.stats_var = tk.StringVar(value=NUMERIC_FEATURES[0])
        om = tk.OptionMenu(stats_frame, self.stats_var, *NUMERIC_FEATURES)
        om.config(bg="white", fg="#2c3e50", font=("Helvetica", 9),
                  highlightthickness=0, relief="groove", width=20)
        om["menu"].config(bg="white", fg="#2c3e50", font=("Helvetica", 9))
        om.pack(padx=6, pady=4)

        tk.Button(stats_frame, text="Show Statistics",
                  command=self._show_statistics,
                  bg="#1a1a1a", fg="white", font=("Helvetica", 9, "bold"),
                  relief="flat", padx=8, pady=4
                  ).pack(padx=6, pady=(0, 6))

        # ── action buttons ───────────────────────────────────────────────────
        btn_frame = tk.Frame(parent, bg="#f0f4f8")
        btn_frame.pack(fill="x", pady=8)

        for col in range(4):
            btn_frame.columnconfigure(col, weight=1)

        btn_specs = [
            ("Run Query",  self._run_query,     "#1a1a1a", 0),
            ("Export CSV", self._export_csv,    "#1a1a1a", 1),
            ("Clear",      self._clear_results, "#1a1a1a", 2),
            ("Quit",       self._quit_app,      "#1a1a1a", 3),
        ]
        for text, cmd, color, col in btn_specs:
            tk.Button(btn_frame, text=text, command=cmd,
                      bg=color, fg="white", font=("Helvetica", 9, "bold"),
                      relief="flat", padx=4, pady=5
                      ).grid(row=0, column=col, sticky="ew", padx=2)

    def _build_right_panel(self, parent):
        tk.Label(parent, text="Query Results", font=("Helvetica", 11, "bold"),
                 bg="#f0f4f8", fg="#2c3e50").pack(anchor="w")

        text_frame = tk.Frame(parent, bg="#f0f4f8")
        text_frame.pack(fill="both", expand=True)

        v_scroll = tk.Scrollbar(text_frame)
        v_scroll.pack(side="right", fill="y")
        h_scroll = tk.Scrollbar(text_frame, orient="horizontal")
        h_scroll.pack(side="bottom", fill="x")

        self.result_text = tk.Text(
            text_frame, wrap="none", font=("Courier", 10),
            bg="white", fg="#2c3e50",
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set,
            state="disabled"
        )
        self.result_text.pack(fill="both", expand=True)
        v_scroll.config(command=self.result_text.yview)
        h_scroll.config(command=self.result_text.xview)

        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(parent, textvariable=self.status_var, bg="#f0f4f8", fg="#2c3e50",
                 font=("Helvetica", 9), anchor="w").pack(fill="x")

    # ──────────────────────────────────── data loading ────────────────────────
    def _load_data(self):
        try:
            self.patient_data = load_patient_data(DATASET_PATH)
            self.engine = QueryEngine(self.patient_data)
            self.feat_stats = FeatureStatistics(self.patient_data)
            self._set_status(f"Dataset loaded: {len(self.patient_data)} patients.")
        except FileNotFoundError as exc:
            messagebox.showerror("File Not Found", str(exc))
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Load Error", f"Failed to load dataset:\n{exc}")
            self.destroy()

    # ──────────────────────────────────── result display ─────────────────────
    def _display(self, text: str):
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("end", text)
        self.result_text.config(state="disabled")

    def _format_result(self, result) -> str:
        """Convert query result (dict / list) to readable text."""
        if isinstance(result, dict):
            lines = [f"  {k:<35} {v}" for k, v in result.items()]
            return "\n".join(lines)
        if isinstance(result, list):
            if not result:
                return "  (no results)"
            if isinstance(result[0], dict):
                keys = list(result[0].keys())
                header = "  " + "  ".join(f"{k:<25}" for k in keys)
                sep = "  " + "-" * (27 * len(keys))
                rows = []
                for item in result:
                    row = "  " + "  ".join(f"{str(item.get(k,'')):<25}" for k in keys)
                    rows.append(row)
                return "\n".join([header, sep] + rows)
            return "\n".join(f"  {r}" for r in result)
        return str(result)

    # ──────────────────────────────────── query runner ────────────────────────
    def _run_query(self):
        selection = self.query_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Query Selected", "Please select a query from the list.")
            return

        index = selection[0]          # 0-based → matches Q1..Q12
        try:
            result = self._execute_query(index + 1)
            self._last_result = result if isinstance(result, list) else [result]
            header = f"{'='*60}\n{QUERY_LABELS[index]}\n{'='*60}\n"
            self._display(header + self._format_result(result))
            self._set_status(f"Query {index+1} executed successfully.")
        except Exception as exc:
            messagebox.showerror("Query Error", str(exc))
            self._set_status(f"Error in Query {index+1}: {exc}")

    def _execute_query(self, query_number: int):
        """Dispatch to the correct QueryEngine method."""
        dispatch = {
            1:  self.engine.query_1_smokers_with_hypertension_age_stats,
            2:  self.engine.query_2_heart_disease_age_glucose,
            3:  self.engine.query_3_gender_hypertension_stroke_age,
            4:  self.engine.query_4_physical_activity_bmi_glucose_stroke_risk,
            5:  self.engine.query_5_residence_stroke_age_stats,
            6:  self.engine.query_6_dietary_habits_stroke,
            7:  self.engine.query_7_hypertension_and_stroke,
            8:  self.engine.query_8_heart_disease_and_stroke,
            9:  self.engine.query_9_sleep_hours_by_stroke,
            10: self._run_query_10,
            11: self.engine.query_11_risk_group_categorisation,
            12: self.engine.query_12_regional_health_summary,
        }
        if query_number not in dispatch:
            raise ValueError(f"Unknown query number: {query_number}")
        return dispatch[query_number]()

    def _run_query_10(self):
        """Collect Q10 filter inputs, validate, and call the engine."""
        def parse_float(val, field_name):
            val = val.strip()
            if not val:
                return None
            try:
                return float(val)
            except ValueError:
                raise ValueError(f"'{field_name}' must be a number (got '{val}').")

        age_min = parse_float(self.e_age_min.get(), "Age min")
        age_max = parse_float(self.e_age_max.get(), "Age max")
        gender  = self.e_gender.get().strip() or None
        smoking = self.e_smoking.get().strip() or None
        region  = self.e_region.get().strip() or None

        if age_min is not None and age_max is not None and age_min > age_max:
            raise ValueError("Age min cannot be greater than Age max.")

        return self.engine.query_10_flexible_filter(
            age_min=age_min, age_max=age_max,
            gender=gender, smoking_status=smoking, region=region
        )

    # ──────────────────────────────────── statistics ──────────────────────────
    def _show_statistics(self):
        feature = self.stats_var.get()
        try:
            stats = self.feat_stats.describe(feature)
            lines = [f"{'='*50}", f"Descriptive Statistics – {feature}", f"{'='*50}"]
            for k, v in stats.items():
                lines.append(f"  {k:<20} {v}")
            self._display("\n".join(lines))
            self._last_result = [stats]
            self._set_status(f"Statistics computed for '{feature}'.")
        except Exception as exc:
            messagebox.showerror("Statistics Error", str(exc))

    # ──────────────────────────────────── export ──────────────────────────────
    def _export_csv(self):
        if not hasattr(self, "_last_result") or not self._last_result:
            messagebox.showwarning("No Data", "Run a query first before exporting.")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save results as CSV"
        )
        if not filepath:
            return
        try:
            self.engine.export_to_csv(self._last_result, filepath)
            self._set_status(f"Results exported to: {os.path.basename(filepath)}")
            messagebox.showinfo("Export Successful", f"Results saved to:\n{filepath}")
        except Exception as exc:
            messagebox.showerror("Export Error", str(exc))

    # ──────────────────────────────────── utility ─────────────────────────────
    def _clear_results(self):
        self._display("")
        self._last_result = []
        self.query_listbox.selection_clear(0, "end")
        self._set_status("Results cleared.")

    def _quit_app(self):
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            self.destroy()

    def _set_status(self, msg: str):
        self.status_var.set(msg)
