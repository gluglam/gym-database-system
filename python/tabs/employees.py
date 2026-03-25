# tabs/employees.py
import tkinter as tk
from tkinter import ttk, messagebox
from tabs.base import BaseTab, simple_form
import sql_queries as Q

class EmployeeTab(BaseTab):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_columns(["ID", "Imię", "Nazwisko", "Rola", "Wynagrodzenie", "Data zatr.", "Przełożony", "Telefony"])
        self.refresh_data()

    def refresh_data(self):
        self.clear_tree()
        rows = self.db.fetch_all(Q.Q_EMPLOYEES_LIST)
        for r in rows:
            self.tree.insert("", "end", values=[
                r["id_osoby"], r["imie"], r["nazwisko"], r["rola"], r["wynagrodzenie"],
                r["data_zatrudnienia"], r["przelozony"], r["telefony"]
            ])

    def search(self):
        self.refresh_data()

    def add_record(self):
        data = simple_form(self, "Dodaj pracownika", [
            ("imie", "Imię"),
            ("nazwisko", "Nazwisko"),
            ("email", "Email"),
            ("data_urodzenia", "Data urodzenia (YYYY-MM-DD)"),
            ("telefon", "Telefon (opcjonalnie, 1 szt.)"),
            ("data_zatrudnienia", "Data zatrudnienia (YYYY-MM-DD)"),
            ("rola", "Rola (np. service/manager/reception/trainer)"),
            ("wynagrodzenie", "Wynagrodzenie (liczba)"),
            ("nadzoruje", "ID przełożonego (puste = brak)"),
        ])
        if not data:
            return

        try:
            boss = int(data["nadzoruje"]) if data["nadzoruje"] else None
        except ValueError:
            messagebox.showwarning("Uwaga", "Pole 'ID przełożonego' musi być liczbą albo puste.")
            return

        try:
            wyn = float(data["wynagrodzenie"])
        except ValueError:
            messagebox.showwarning("Uwaga", "Wynagrodzenie musi być liczbą.")
            return

        try:
            with self.db.tx():
                # 1) Osoba
                self.db.execute("""
                    INSERT INTO Osoba(imie, nazwisko, email, data_urodzenia, stworzone_dnia)
                    VALUES(?, ?, ?, ?, date('now'));
                """, (data["imie"], data["nazwisko"], data["email"], data["data_urodzenia"]))

                # 2) (opcjonalnie) telefon – uwaga: nr_tel jest PK globalnie
                if data["telefon"]:
                    self.db.execute("""
                        INSERT INTO Nr_telefonu(nr_tel, id_osoby)
                        VALUES(?, last_insert_rowid());
                    """, (data["telefon"],))

                # 3) Pracownik – PK=FK do Osoba
                self.db.execute("""
                    INSERT INTO Pracownik(id_osoby, data_zatrudnienia, rola, wynagrodzenie, nadzoruje)
                    VALUES(last_insert_rowid(), ?, ?, ?, ?);
                """, (data["data_zatrudnienia"], data["rola"], wyn, boss))

            self.refresh_data()
            messagebox.showinfo("OK", "Dodano pracownika.")
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def edit_record(self):
        vals = self.selected_row_values()
        if not vals:
            return
        emp_id = vals[0]

        cur = self.db.fetch_one("""
            SELECT p.id_osoby, o.imie, o.nazwisko, p.rola, p.wynagrodzenie, p.data_zatrudnienia, p.nadzoruje
            FROM Pracownik p JOIN Osoba o ON o.id_osoby=p.id_osoby
            WHERE p.id_osoby=?
        """, (emp_id,))
        data = simple_form(self, "Edytuj pracownika", [
            ("rola", "Rola (np. service/manager/reception/trainer)"),
            ("wynagrodzenie", "Wynagrodzenie (liczba)"),
            ("nadzoruje", "ID przełożonego (puste = brak)"),
        ], initial={
            "rola": cur["rola"],
            "wynagrodzenie": cur["wynagrodzenie"],
            "nadzoruje": "" if cur["nadzoruje"] is None else cur["nadzoruje"]
        })
        if not data:
            return

        try:
            boss = int(data["nadzoruje"]) if data["nadzoruje"] else None
            wyn = float(data["wynagrodzenie"])
            with self.db.tx():
                self.db.execute("""
                    UPDATE Pracownik SET rola=?, wynagrodzenie=?, nadzoruje=?
                    WHERE id_osoby=?
                """, (data["rola"], wyn, boss, emp_id))
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def delete_record(self):
        vals = self.selected_row_values()
        if not vals:
            return
        emp_id = vals[0]
        if not messagebox.askyesno("Potwierdź", f"Usunąć pracownika (Osoba ID={emp_id})?\n"
                                               f"To skasuje też rekord Pracownik i ewentualne dane zależne (kaskady)."):
            return
        try:
            with self.db.tx():
                # Najbezpieczniej usuwać Osoba – reszta poleci kaskadą
                self.db.execute("DELETE FROM Osoba WHERE id_osoby=?", (emp_id,))
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Błąd", str(e))
