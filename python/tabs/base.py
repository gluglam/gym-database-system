# tabs/base.py
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from database import DB


class BaseTab(ttk.Frame):
    """
    Bazowa zakładka: tabela + (opcjonalnie) filtry + CRUD.
    Dzieci nadpisują: refresh_data(), search(), add_record(), edit_record(), delete_record()
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DB()
        self.pack(fill="both", expand=True, padx=10, pady=10)
        self._build_ui()

        # Sprzątanie (ważne na Windows – blokady pliku .db)
        self.bind("<Destroy>", self._on_destroy)

    def _on_destroy(self, _event=None):
        # Tk wywołuje Destroy także dla dzieci; pilnujemy, aby zamknąć tylko raz.
        if getattr(self, "_db_closed", False):
            return
        self._db_closed = True
        try:
            self.db.close()
        except Exception:
            pass

    def _build_ui(self):
        self.search_frame = ttk.LabelFrame(self, text="Wyszukiwanie / Filtry")
        self.search_frame.pack(fill="x", pady=6)

        self.controls_frame = ttk.Frame(self)
        self.controls_frame.pack(fill="x", pady=6)

        self.tree = ttk.Treeview(self, show="headings", selectmode="browse")
        self.tree.pack(fill="both", expand=True)

        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)

        btns = ttk.Frame(self)
        btns.pack(fill="x", pady=8)
        ttk.Button(btns, text="Dodaj", command=self.add_record).pack(side="left", padx=4)
        ttk.Button(btns, text="Edytuj", command=self.edit_record).pack(side="left", padx=4)
        ttk.Button(btns, text="Usuń", command=self.delete_record).pack(side="left", padx=4)
        ttk.Button(btns, text="Odśwież", command=self.refresh_data).pack(side="right", padx=4)

        self.tree.bind("<Double-1>", lambda _e: self.edit_record())

    def setup_columns(self, cols: list[str]):
        self.tree["columns"] = cols
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=140, anchor="w")

    def clear_tree(self):
        for r in self.tree.get_children():
            self.tree.delete(r)

    def selected_row_values(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])["values"]

    # --- do nadpisania ---
    def refresh_data(self): ...
    def search(self): ...
    def add_record(self): ...
    def edit_record(self): ...
    def delete_record(self): ...


def simple_form(parent, title: str, fields: list[tuple[str, str]], initial: dict | None = None):
    """
    fields: list[(key, label)]
    initial: dict key->value
    returns dict or None
    """
    top = tk.Toplevel(parent)
    top.title(title)
    top.grab_set()

    frm = ttk.Frame(top, padding=10)
    frm.pack(fill="both", expand=True)

    vars_ = {}
    for key, label in fields:
        ttk.Label(frm, text=label).pack(anchor="w", pady=(6, 0))
        v = tk.StringVar(value="" if not initial else str(initial.get(key, "")))
        ent = ttk.Entry(frm, textvariable=v, width=44)
        ent.pack(fill="x")
        vars_[key] = v

    result = {"ok": False}

    def ok():
        result["ok"] = True
        top.destroy()

    def cancel():
        top.destroy()

    btns = ttk.Frame(frm)
    btns.pack(fill="x", pady=10)
    ttk.Button(btns, text="Anuluj", command=cancel).pack(side="right", padx=5)
    ttk.Button(btns, text="Zapisz", command=ok).pack(side="right")

    top.wait_window()
    if not result["ok"]:
        return None
    return {k: v.get().strip() for k, v in vars_.items()}
