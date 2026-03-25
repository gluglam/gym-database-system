# tabs/members.py
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from tabs.base import BaseTab, simple_form
import sql_queries as Q


STATUS_LABEL_TO_CODE = {
    "": "",
    "Aktywny": "Aktywny",
    "Zawieszony": "Zawieszony",
    "Nieaktywny": "Nieaktywny",
}
STATUS_CODE_TO_LABEL = {v: k for k, v in STATUS_LABEL_TO_CODE.items() if v}


class MemberTab(BaseTab):
    def __init__(self, parent):
        super().__init__(parent)

        ttk.Label(self.search_frame, text="Fraza (nazwisko/email):").pack(side="left", padx=5)
        self.term = tk.StringVar()
        ttk.Entry(self.search_frame, textvariable=self.term, width=24).pack(side="left", padx=5)

        ttk.Label(self.search_frame, text="Status członka:").pack(side="left", padx=5)
        self.status = tk.StringVar(value="")
        ttk.Combobox(
            self.search_frame,
            textvariable=self.status,
            values=list(STATUS_LABEL_TO_CODE.keys()),
            width=12,
            state="readonly",
        ).pack(side="left", padx=5)

        ttk.Button(self.search_frame, text="Szukaj", command=self.search).pack(side="left", padx=5)
        ttk.Button(self.search_frame, text="Reset", command=self.refresh_data).pack(side="left", padx=5)

        self.setup_columns(["ID", "Imię", "Nazwisko", "Email", "Telefony", "Dołączył", "Status", "Karnet dziś"])
        self.refresh_data()

    def refresh_data(self):
        self.clear_tree()
        rows = self.db.fetch_all(Q.Q_MEMBERS_LIST)
        for r in rows:
            self.tree.insert(
                "",
                "end",
                values=[
                    r["id_osoby"],
                    r["imie"],
                    r["nazwisko"],
                    r["email"],
                    r["telefony"],
                    r["data_dolaczenia"],
                    STATUS_CODE_TO_LABEL.get(r["status_czlonka"], r["status_czlonka"]),
                    r["status_aktywny_karnet"],
                ],
            )

    def search(self):
        self.clear_tree()
        term = self.term.get().strip()
        stat_code = STATUS_LABEL_TO_CODE.get(self.status.get().strip(), "")
        rows = self.db.fetch_all(Q.Q_MEMBERS_SEARCH, (f"%{term}%", f"%{term}%", stat_code, stat_code))
        for r in rows:
            self.tree.insert(
                "",
                "end",
                values=[
                    r["id_osoby"],
                    r["imie"],
                    r["nazwisko"],
                    r["email"],
                    r["telefony"],
                    r["data_dolaczenia"],
                    STATUS_CODE_TO_LABEL.get(r["status"], r["status"]),
                    "",
                ],
            )

    def add_record(self):
        data = simple_form(
            self,
            "Dodaj członka",
            [
                ("imie", "Imię"),
                ("nazwisko", "Nazwisko"),
                ("email", "Email"),
                ("data_urodzenia", "Data urodzenia (YYYY-MM-DD)"),
                ("telefony", "Telefony (CSV, opcjonalnie)"),
            ],
        )
        if not data:
            return

        phones = [x.strip() for x in data["telefony"].split(",") if x.strip()]

        try:
            with self.db.tx():
                self.db.execute(
                    Q.Q_MEMBER_ADD_OSOBA,
                    (data["imie"], data["nazwisko"], data["email"], data["data_urodzenia"]),
                )
                for p in phones:
                    self.db.execute(Q.Q_MEMBER_ADD_PHONE, (p,))
                self.db.execute(Q.Q_MEMBER_ADD_CZLONEK)

            self.refresh_data()
            messagebox.showinfo("OK", "Dodano członka.")
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def edit_record(self):
        vals = self.selected_row_values()
        if not vals:
            return
        member_id = vals[0]

        current = self.db.fetch_one(
            """
            SELECT o.id_osoby, o.imie, o.nazwisko, o.email, o.data_urodzenia, c.status
            FROM Osoba o
            JOIN Czlonek c ON c.id_osoby = o.id_osoby
            WHERE o.id_osoby = ?
            """,
            (member_id,),
        )
        if not current:
            return

        phones = self.db.fetch_all(
            "SELECT nr_tel FROM Nr_telefonu WHERE id_osoby=? ORDER BY nr_tel",
            (member_id,),
        )
        phones_str = ", ".join([p["nr_tel"] for p in phones])

        data = simple_form(
            self,
            "Edytuj członka",
            [
                ("imie", "Imię"),
                ("nazwisko", "Nazwisko"),
                ("email", "Email"),
                ("data_urodzenia", "Data urodzenia (YYYY-MM-DD)"),
                ("status", "Status (Aktywny/Zawieszony/Nieaktywny)"),
                ("telefony", "Telefony (CSV, np. 123,456)"),
            ],
            initial={
                "imie": current["imie"],
                "nazwisko": current["nazwisko"],
                "email": current["email"],
                "data_urodzenia": current["data_urodzenia"],
                "status": current["status"],
                "telefony": phones_str,
            },
        )
        if not data:
            return

        nums = [x.strip() for x in data["telefony"].split(",") if x.strip()]

        try:
            with self.db.tx():
                self.db.execute(
                    """
                    UPDATE Osoba
                    SET imie=?, nazwisko=?, email=?, data_urodzenia=?
                    WHERE id_osoby=?
                    """,
                    (data["imie"], data["nazwisko"], data["email"], data["data_urodzenia"], member_id),
                )
                self.db.execute("UPDATE Czlonek SET status=? WHERE id_osoby=?", (data["status"], member_id))

                # telefony: usuń i wstaw z CSV (PK=nr_tel globalnie)
                self.db.execute("DELETE FROM Nr_telefonu WHERE id_osoby=?", (member_id,))
                for n in nums:
                    self.db.execute("INSERT INTO Nr_telefonu(nr_tel, id_osoby) VALUES(?,?)", (n, member_id))

            self.refresh_data()
            messagebox.showinfo("OK", "Zapisano zmiany.")
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def delete_record(self):
        vals = self.selected_row_values()
        if not vals:
            return
        member_id = vals[0]
        if not messagebox.askyesno("Potwierdź", f"Usunąć członka (Osoba ID={member_id})?"):
            return
        try:
            with self.db.tx():
                self.db.execute(Q.Q_MEMBER_DELETE, (member_id,))
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Błąd", str(e))
