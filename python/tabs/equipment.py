# tabs/equipment.py
import tkinter as tk
from tkinter import ttk, messagebox
from tabs.base import BaseTab, simple_form
import sql_queries as Q

class EquipmentTab(BaseTab):
    def __init__(self, parent):
        super().__init__(parent)

        ttk.Button(self.search_frame, text="Pokaż sprzęt z otwartymi zgłoszeniami",
                   command=self.show_open_tickets).pack(side="left", padx=6)

        self.setup_columns(["ID", "Nazwa", "Kategoria", "Nr seryjny", "Data zakupu", "Status"])
        self.refresh_data()

    def refresh_data(self):
        self.clear_tree()
        self.setup_columns(["ID", "Nazwa", "Kategoria", "Nr seryjny", "Data zakupu", "Status"])
        rows = self.db.fetch_all("""
            SELECT id_sprzetu, nazwa, kategoria, nr_seryjny, data_zakupu, status
            FROM Sprzet
            ORDER BY kategoria, nazwa;
        """)
        for r in rows:
            self.tree.insert("", "end", values=[r["id_sprzetu"], r["nazwa"], r["kategoria"], r["nr_seryjny"], r["data_zakupu"], r["status"]])

    def show_open_tickets(self):
        self.clear_tree()
        rows = self.db.fetch_all(Q.Q_EQUIPMENT_OPEN_TICKETS)
        # pokażemy tu inne kolumny „raportowe”
        self.setup_columns(["ID", "Nazwa", "Kategoria", "Status", "Otwarte zgłoszenia"])
        for r in rows:
            self.tree.insert("", "end", values=[r["id_sprzetu"], r["nazwa"], r["kategoria"], r["status_sprzetu"], r["otwartych_zgloszen"]])

    def search(self):
        self.refresh_data()

    def add_record(self):
        data = simple_form(self, "Dodaj sprzęt", [
            ("nazwa", "Nazwa"),
            ("kategoria", "Kategoria (cardio/strength/...)"),
            ("nr_seryjny", "Nr seryjny"),
            ("data_zakupu", "Data zakupu (YYYY-MM-DD)"),
            ("status", "Status (in_service/out_of_service/retired)"),
        ])
        if not data:
            return
        try:
            with self.db.tx():
                self.db.execute("""
                    INSERT INTO Sprzet(nazwa,kategoria,nr_seryjny,data_zakupu,status)
                    VALUES(?,?,?,?,?)
                """, (data["nazwa"], data["kategoria"], data["nr_seryjny"], data["data_zakupu"], data["status"]))
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def edit_record(self):
        vals = self.selected_row_values()
        if not vals:
            return
        sid = vals[0]
        cur = self.db.fetch_one("SELECT * FROM Sprzet WHERE id_sprzetu=?", (sid,))
        data = simple_form(self, "Edytuj sprzęt", [
            ("nazwa", "Nazwa"),
            ("kategoria", "Kategoria"),
            ("nr_seryjny", "Nr seryjny"),
            ("data_zakupu", "Data zakupu"),
            ("status", "Status"),
        ], initial=dict(cur))
        if not data:
            return
        try:
            with self.db.tx():
                self.db.execute("""
                    UPDATE Sprzet SET nazwa=?, kategoria=?, nr_seryjny=?, data_zakupu=?, status=?
                    WHERE id_sprzetu=?
                """, (data["nazwa"], data["kategoria"], data["nr_seryjny"], data["data_zakupu"], data["status"], sid))
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def delete_record(self):
        vals = self.selected_row_values()
        if not vals:
            return
        sid = vals[0]
        if not messagebox.askyesno("Potwierdź", f"Usunąć sprzęt ID={sid}?"):
            return
        try:
            with self.db.tx():
                self.db.execute("DELETE FROM Sprzet WHERE id_sprzetu=?", (sid,))
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Błąd", str(e))
