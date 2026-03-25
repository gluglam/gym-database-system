# tabs/schedule.py
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from tabs.base import BaseTab, simple_form
import sql_queries as Q


class ScheduleTab(BaseTab):
    def __init__(self, parent):
        super().__init__(parent)

        ttk.Label(self.search_frame, text="Członek:").pack(side="left", padx=4)
        self.member_var = tk.StringVar()
        self.member_cb = ttk.Combobox(self.search_frame, textvariable=self.member_var, width=28, state="readonly")
        self.member_cb.pack(side="left", padx=4)

        ttk.Label(self.search_frame, text="Sesja:").pack(side="left", padx=4)
        self.session_var = tk.StringVar()
        self.session_cb = ttk.Combobox(self.search_frame, textvariable=self.session_var, width=40, state="readonly")
        self.session_cb.pack(side="left", padx=4)

        ttk.Button(self.search_frame, text="Zapisz (1 SQL)", command=self.signup_fancy).pack(side="left", padx=6)
        ttk.Button(self.search_frame, text="Prawie pełne (>=80%)", command=self.show_nearly_full).pack(side="left", padx=6)
        ttk.Button(self.search_frame, text="Reset", command=self.refresh_data).pack(side="left", padx=6)

        self.setup_columns(["ID", "Typ", "Trener", "Start", "Sala", "Limit", "Zapisanych", "Wolnych"])
        self._reload_lookups()
        self.refresh_data()

    def _reload_lookups(self):
        members = self.db.fetch_all(
            """
            SELECT c.id_osoby, o.nazwisko || ' ' || o.imie AS nazwa
            FROM Czlonek c
            JOIN Osoba o ON o.id_osoby = c.id_osoby
            ORDER BY o.nazwisko, o.imie
            """
        )
        self._member_map = {f'{m["nazwa"]} (ID={m["id_osoby"]})': int(m["id_osoby"]) for m in members}
        self.member_cb["values"] = list(self._member_map.keys())
        if self.member_cb["values"] and not self.member_var.get():
            self.member_var.set(self.member_cb["values"][0])

        sessions = self.db.fetch_all(
            """
            SELECT sz.id_sesji,
                   tz.nazwa AS typ,
                   sz.czas_rozpoczecia AS start,
                   sz.sala AS sala
            FROM Sesja_zajec sz
            JOIN Typ_zajec tz ON tz.id_typu = sz.id_typu
            WHERE sz.status IN ('scheduled', 'open')
            ORDER BY sz.czas_rozpoczecia DESC
            LIMIT 200
            """
        )
        self._session_map = {
            f'{s["typ"]} | {s["start"]} | sala {s["sala"]} (ID={s["id_sesji"]})': int(s["id_sesji"])
            for s in sessions
        }
        self.session_cb["values"] = list(self._session_map.keys())
        if self.session_cb["values"] and not self.session_var.get():
            self.session_var.set(self.session_cb["values"][0])

    def refresh_data(self):
        self.clear_tree()
        self._reload_lookups()
        rows = self.db.fetch_all(Q.Q_SCHEDULE_LIST)
        for r in rows:
            self.tree.insert(
                "",
                "end",
                values=[
                    r["id_sesji"],
                    r["typ_zajec"],
                    r["trener"],
                    r["czas_rozpoczecia"],
                    r["sala"],
                    r["limit_miejsc"],
                    r["zapisanych"],
                    r["wolnych"],
                ],
            )

    def show_nearly_full(self):
        self.clear_tree()
        self.setup_columns(["ID", "Typ", "Start", "Limit", "Zapisanych", "Procent"])
        rows = self.db.fetch_all(Q.Q_NEARLY_FULL)
        for r in rows:
            self.tree.insert(
                "",
                "end",
                values=[r["id_sesji"], r["nazwa"], r["czas_rozpoczecia"], r["liczebnosc"], r["zapisanych"], r["procent"]],
            )

    def signup_fancy(self):
        if self.member_var.get() not in self._member_map or self.session_var.get() not in self._session_map:
            messagebox.showwarning("Uwaga", "Wybierz członka i sesję.")
            return

        mid = self._member_map[self.member_var.get()]
        sid = self._session_map[self.session_var.get()]

        try:
            with self.db.tx():
                cur = self.db.execute(Q.Q_SIGNUP_FANCY, (mid, sid, mid, mid, sid, mid, sid, sid, sid, sid))
                if cur.rowcount == 0:
                    messagebox.showwarning("Brak", "Nie spełniono warunków zapisu (karnet, status, limit, duplikat).")
                    return
            self.refresh_data()
            messagebox.showinfo("OK", "Zapisano na zajęcia.")
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def search(self):
        self.refresh_data()

    def add_record(self):
        data = simple_form(
            self,
            "Dodaj sesję zajęć",
            [
                ("czas_rozpoczecia", "Czas rozpoczęcia (YYYY-MM-DD HH:MM)"),
                ("sala", "Sala"),
                ("liczebnosc", "Limit miejsc (liczba)"),
                ("status", "Status (scheduled/open/cancelled)"),
                ("id_typu", "ID typu zajęć (na razie PK)"),
                ("id_trenera", "ID trenera (opcjonalnie)"),
            ],
        )
        if not data:
            return
        try:
            limit_ = int(data["liczebnosc"])
            id_typu = int(data["id_typu"])
            id_trenera = int(data["id_trenera"]) if data["id_trenera"] else None
        except ValueError:
            messagebox.showwarning("Uwaga", "liczebnosc/id_typu/id_trenera muszą być liczbami (id_trenera może być puste).")
            return

        try:
            with self.db.tx():
                self.db.execute(
                    """
                    INSERT INTO Sesja_zajec(czas_rozpoczecia, sala, liczebnosc, status, id_typu, id_osoby)
                    VALUES(?, ?, ?, ?, ?, ?)
                    """,
                    (data["czas_rozpoczecia"], data["sala"], limit_, data["status"], id_typu, id_trenera),
                )
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def edit_record(self):
        vals = self.selected_row_values()
        if not vals:
            return
        sid = vals[0]
        cur = self.db.fetch_one("SELECT * FROM Sesja_zajec WHERE id_sesji=?", (sid,))
        if not cur:
            return

        data = simple_form(
            self,
            "Edytuj sesję zajęć",
            [
                ("czas_rozpoczecia", "Czas rozpoczęcia (YYYY-MM-DD HH:MM)"),
                ("sala", "Sala"),
                ("liczebnosc", "Limit miejsc (liczba)"),
                ("status", "Status (scheduled/open/cancelled)"),
                ("id_typu", "ID typu zajęć"),
                ("id_osoby", "ID trenera (opcjonalnie)"),
            ],
            initial=dict(cur),
        )
        if not data:
            return

        try:
            limit_ = int(data["liczebnosc"])
            id_typu = int(data["id_typu"])
            id_trenera = int(data["id_osoby"]) if data["id_osoby"] else None
        except ValueError:
            messagebox.showwarning("Uwaga", "liczebnosc/id_typu/id_osoby muszą być liczbami (id_osoby może być puste).")
            return

        try:
            with self.db.tx():
                self.db.execute(
                    """
                    UPDATE Sesja_zajec
                    SET czas_rozpoczecia=?, sala=?, liczebnosc=?, status=?, id_typu=?, id_osoby=?
                    WHERE id_sesji=?
                    """,
                    (data["czas_rozpoczecia"], data["sala"], limit_, data["status"], id_typu, id_trenera, sid),
                )
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def delete_record(self):
        vals = self.selected_row_values()
        if not vals:
            return
        sid = vals[0]
        if not messagebox.askyesno("Potwierdź", f"Usunąć sesję ID={sid}? (Zapisani polecą kaskadą)"):
            return
        try:
            with self.db.tx():
                self.db.execute("DELETE FROM Sesja_zajec WHERE id_sesji=?", (sid,))
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Błąd", str(e))
