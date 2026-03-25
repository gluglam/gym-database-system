# tabs/reports.py
from __future__ import annotations

import csv
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import sql_queries as Q
from database import DB, DB_PATH


class ReportsTab(ttk.Frame):
    """
    Zakładka raportów:
    1) "Raporty SQL" – uruchamianie zapytań z All.sql i prezentacja w tabeli + eksport CSV
    2) "JasperReports" – generowanie PDF przez JasperStarter (wymaga przygotowanych .jasper)
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DB()
        self.pack(fill="both", expand=True, padx=10, pady=10)

        # Ścieżki do narzędzi (możesz dostosować do swojego projektu)
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project/
        self.jasperstarter = os.path.join(base, "tools", "jaspersoft", "jasperstarter.jar")
        self.sqlitejdbc = os.path.join(base, "tools", "jaspersoft", "sqlite-jdbc-3.49.1.0.jar")
        self.reports_dir = os.path.join(base, "reports_jrxml")

        self._build_ui()

    def _build_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        self.sql_tab = ttk.Frame(nb)
        self.jasper_tab = ttk.Frame(nb)
        nb.add(self.sql_tab, text="Raporty SQL")
        nb.add(self.jasper_tab, text="JasperReports")

        self._build_sql_reports()
        self._build_jasper_reports()

    # =========================
    # Raporty SQL
    # =========================
    def _build_sql_reports(self):
        top = ttk.LabelFrame(self.sql_tab, text="Wybierz raport (zapytanie SQL)")
        top.pack(fill="x", pady=6)

        self.report_defs = [
            ("Członkowie bez zakupów 90 dni (NOT EXISTS)", Q.Q_INACTIVE_90D, ("",)),
            ("VIP: członkowie >= X zakupów w roku (GROUP BY/HAVING)", Q.Q_VIP_MEMBERS_BY_YEAR, ("2025", "2")),
            ("Karnety wygasające w 14 dni", Q.Q_EXPIRING_PASSES_14D, ("",)),
            ("Przychody: miesiąc+metoda (GROUP BY/HAVING)", Q.Q_REVENUE_REPORT, ("2025", "0")),
            ("Top plany w roku (GROUP BY/HAVING)", Q.Q_TOP_PLANS, ("2025", "1")),
            ("Podejrzane płatności: paid < cena planu (JOIN)", Q.Q_SUSPICIOUS_PAYMENTS, ("",)),
            ("ALL-ekwiwalent: zakup > MAX(cena_bazowa)", Q.Q_PURCHASES_OVER_ALL_PLAN_PRICES, ("",)),
            ("ANY-ekwiwalent: płatność > MIN(cena_bazowa)", Q.Q_PAYMENTS_OVER_ANY_PLAN_PRICE, ("",)),
            ("Zgłoszenia serwisowe w toku", Q.Q_SERVICE_IN_PROGRESS, ("",)),
        ]

        ttk.Label(top, text="Raport:").pack(side="left", padx=6)
        self.rep_var = tk.StringVar(value=self.report_defs[0][0])
        self.rep_cb = ttk.Combobox(top, textvariable=self.rep_var, values=[r[0] for r in self.report_defs], width=54, state="readonly")
        self.rep_cb.pack(side="left", padx=6)

        ttk.Button(top, text="Uruchom", command=self.run_sql_report).pack(side="left", padx=6)
        ttk.Button(top, text="Eksport CSV", command=self.export_csv).pack(side="left", padx=6)

        self.params_frame = ttk.LabelFrame(self.sql_tab, text="Parametry (dla raportów parametryzowanych)")
        self.params_frame.pack(fill="x", pady=6)

        ttk.Label(self.params_frame, text="P1:").pack(side="left", padx=6)
        self.p1 = tk.StringVar()
        ttk.Entry(self.params_frame, textvariable=self.p1, width=16).pack(side="left", padx=4)

        ttk.Label(self.params_frame, text="P2:").pack(side="left", padx=6)
        self.p2 = tk.StringVar()
        ttk.Entry(self.params_frame, textvariable=self.p2, width=16).pack(side="left", padx=4)

        ttk.Label(self.params_frame, text="(pozostaw puste, jeśli raport nie wymaga)").pack(side="left", padx=10)

        # tabela wyników
        self.tree = ttk.Treeview(self.sql_tab, show="headings", selectmode="browse")
        self.tree.pack(fill="both", expand=True, pady=6)

        sb = ttk.Scrollbar(self.sql_tab, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)

        self._last_rows = []
        self._last_cols = []

        # init parametrów domyślnych
        self._sync_defaults()

        self.rep_cb.bind("<<ComboboxSelected>>", lambda _e: self._sync_defaults())

    def _sync_defaults(self):
        name = self.rep_var.get()
        for n, _sql, defaults in self.report_defs:
            if n == name:
                d = list(defaults) + ["", ""]
                self.p1.set(d[0])
                self.p2.set(d[1])
                break

    def run_sql_report(self):
        name = self.rep_var.get()
        sql = None
        defaults = ("",)
        for n, s, d in self.report_defs:
            if n == name:
                sql = s
                defaults = d
                break
        if not sql:
            return

        # parametry: jeśli w SQL są ?, bierzemy P1/P2
        params = []
        if "?" in sql:
            if sql.count("?") >= 1:
                if self.p1.get().strip() == "" and len(defaults) >= 1 and defaults[0] != "":
                    self.p1.set(defaults[0])
                params.append(self.p1.get().strip())
            if sql.count("?") >= 2:
                if self.p2.get().strip() == "" and len(defaults) >= 2 and defaults[1] != "":
                    self.p2.set(defaults[1])
                params.append(self.p2.get().strip())

        try:
            rows = self.db.fetch_all(sql, tuple(params))
            self._render_rows(rows)
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def _render_rows(self, rows):
        self.tree.delete(*self.tree.get_children())
        if not rows:
            self.tree["columns"] = []
            self._last_rows, self._last_cols = [], []
            return

        cols = rows[0].keys()
        self.tree["columns"] = list(cols)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=150, anchor="w")

        for r in rows:
            self.tree.insert("", "end", values=[r[c] for c in cols])

        self._last_rows = rows
        self._last_cols = list(cols)

    def export_csv(self):
        if not self._last_rows or not self._last_cols:
            messagebox.showwarning("Brak", "Najpierw uruchom raport SQL.")
            return

        fp = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Zapisz CSV"
        )
        if not fp:
            return

        try:
            with open(fp, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f, delimiter=";")
                w.writerow(self._last_cols)
                for r in self._last_rows:
                    w.writerow([r[c] for c in self._last_cols])
            messagebox.showinfo("OK", f"Zapisano: {fp}")
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    # =========================
    # JasperReports
    # =========================
    def _build_jasper_reports(self):
        frm = ttk.LabelFrame(self.jasper_tab, text="JasperReports (JasperStarter)")
        frm.pack(fill="x", pady=10)

        ttk.Label(frm, text="Rok (YEAR):").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.year = tk.StringVar(value="2025")
        ttk.Entry(frm, textvariable=self.year, width=10).grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(frm, text="Min suma (MIN_SUM):").grid(row=0, column=2, sticky="w", padx=6, pady=4)
        self.min_sum = tk.StringVar(value="0")
        ttk.Entry(frm, textvariable=self.min_sum, width=10).grid(row=0, column=3, sticky="w", padx=6, pady=4)

        ttk.Label(frm, text="Min zakupy VIP (MIN_CNT):").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.min_cnt = tk.StringVar(value="2")
        ttk.Entry(frm, textvariable=self.min_cnt, width=10).grid(row=1, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(frm, text="Min HAVING TopPlany (MIN_PURCH):").grid(row=1, column=2, sticky="w", padx=6, pady=4)
        self.min_purch = tk.StringVar(value="1")
        ttk.Entry(frm, textvariable=self.min_purch, width=10).grid(row=1, column=3, sticky="w", padx=6, pady=4)

        btns = ttk.Frame(frm)
        btns.grid(row=2, column=0, columnspan=4, sticky="w", padx=6, pady=8)

        ttk.Button(btns, text="Revenue.pdf", command=lambda: self.run_jasper("revenue.jasper", {"YEAR": self.year.get(), "MIN_SUM": self.min_sum.get()})).pack(side="left", padx=4)
        ttk.Button(btns, text="VIP.pdf", command=lambda: self.run_jasper("vip_members.jasper", {"YEAR": self.year.get(), "MIN_CNT": self.min_cnt.get()})).pack(side="left", padx=4)
        ttk.Button(btns, text="TopPlany.pdf", command=lambda: self.run_jasper("top_plans.jasper", {"YEAR": self.year.get(), "MIN_PURCH": self.min_purch.get()})).pack(side="left", padx=4)
        ttk.Button(btns, text="Wygasające14dni.pdf", command=lambda: self.run_jasper("expiring_14d.jasper", {})).pack(side="left", padx=4)

    def run_jasper(self, jasper_filename: str, params: dict):
        try:
            jasper_file = os.path.join(self.reports_dir, jasper_filename)
            out_dir = os.path.join(self.reports_dir, "out")
            os.makedirs(out_dir, exist_ok=True)
            out_base = os.path.join(out_dir, os.path.splitext(jasper_filename)[0])

            pdf = self._run_jasper(jasper_file=jasper_file, out_base=out_base, params=params)
            messagebox.showinfo("OK", f"Wygenerowano: {pdf}")

            # Otwórz plik (Windows / macOS / Linux)
            self._open_file(pdf)
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def _run_jasper(self, jasper_file: str, out_base: str, params: dict) -> str:
        if not os.path.exists(self.jasperstarter):
            raise FileNotFoundError("Brak jasperstarter.jar (tools/jaspersoft).")
        if not os.path.exists(self.sqlitejdbc):
            raise FileNotFoundError("Brak sqlite-jdbc.jar (tools/jaspersoft).")
        if not os.path.exists(jasper_file):
            raise FileNotFoundError(f"Brak pliku raportu: {jasper_file}")

        cmd = [
            "java", "-jar", self.jasperstarter,
            "process", jasper_file,
            "-o", out_base,
            "-f", "pdf",
            "-t", "jdbc",
            "--jdbc-driver", self.sqlitejdbc,
            "--jdbc-class", "org.sqlite.JDBC",
            "-u", f"jdbc:sqlite:{DB_PATH}",
            "-n", "",
            "-p",
        ]
        for k, v in params.items():
            cmd.append(f"{k}={v}")

        subprocess.run(cmd, check=True)
        return out_base + ".pdf"

    @staticmethod
    def _open_file(path: str):
        if sys.platform.startswith("win"):
            os.startfile(path)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False)
