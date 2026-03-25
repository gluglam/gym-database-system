# tabs/purchases.py
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from tabs.base import BaseTab, simple_form
import sql_queries as Q


PAY_STATUS = ["Opłacona", "Oczekująca", "Odrzucona"]
PAY_METHODS = ["Karta", "Gotówka", "Blik", "Przelew"]
PURCHASE_STATUS = ["Aktywny", "Opłacony", "Wygasły", "Anulowany"]


class PurchaseTab(BaseTab):
    def __init__(self, parent):
        super().__init__(parent)

        # Wymóg z projektu: UI nie powinno zmuszać do pamiętania PK.
        # Dlatego wybór członka i planu robimy przez combobox z nazwą + ID w tle.

        ttk.Label(self.search_frame, text="Członek:").pack(side="left", padx=4)
        self.member_var = tk.StringVar()
        self.member_cb = ttk.Combobox(self.search_frame, textvariable=self.member_var, width=28, state="readonly")
        self.member_cb.pack(side="left", padx=4)

        ttk.Label(self.search_frame, text="Plan:").pack(side="left", padx=4)
        self.plan_var = tk.StringVar()
        self.plan_cb = ttk.Combobox(self.search_frame, textvariable=self.plan_var, width=20, state="readonly")
        self.plan_cb.pack(side="left", padx=4)

        ttk.Label(self.search_frame, text="Metoda:").pack(side="left", padx=4)
        self.method = tk.StringVar(value=PAY_METHODS[0])
        ttk.Combobox(self.search_frame, textvariable=self.method, values=PAY_METHODS, width=10, state="readonly").pack(
            side="left", padx=4
        )

        ttk.Label(self.search_frame, text="Status płatności:").pack(side="left", padx=4)
        self.pay_status = tk.StringVar(value=PAY_STATUS[0])
        ttk.Combobox(
            self.search_frame, textvariable=self.pay_status, values=PAY_STATUS, width=10, state="readonly"
        ).pack(side="left", padx=4)

        ttk.Button(self.search_frame, text="Sprzedaj karnet", command=self.sell_pass).pack(side="left", padx=10)
        ttk.Button(self.search_frame, text="Odśwież", command=self.refresh_data).pack(side="left", padx=6)

        self.setup_columns(["ID zakupu", "Data zakupu", "Członek", "Plan", "Start", "Koniec", "Cena", "Status"])
        self._reload_lookups()
        self.refresh_data()

    # ---------- lookups ----------
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

        plans = self.db.fetch_all("SELECT id_planu, nazwa, dlugosc_dni, cena_bazowa FROM Plan_karnetu ORDER BY nazwa;")
        self._plan_map = {
            f'{p["nazwa"]} {p["dlugosc_dni"]}d ({p["cena_bazowa"]} zł) (ID={p["id_planu"]})': int(p["id_planu"])
            for p in plans
        }
        self.plan_cb["values"] = list(self._plan_map.keys())
        if self.plan_cb["values"] and not self.plan_var.get():
            self.plan_var.set(self.plan_cb["values"][0])

    def refresh_data(self):
        self.clear_tree()
        self._reload_lookups()

        rows = self.db.fetch_all(
            """
            SELECT zk.id_zakupu, zk.data_zakupu,
                   o.nazwisko || ' ' || o.imie AS czlonek,
                   pk.nazwa AS plan,
                   zk.data_rozpoczecia, zk.data_zakonczenia,
                   zk.cena_koncowa, zk.status
            FROM Zakup_karnetu zk
            JOIN Plan_karnetu pk ON pk.id_planu = zk.id_planu
            JOIN Osoba o ON o.id_osoby = zk.id_osoby
            ORDER BY zk.data_zakupu DESC, zk.id_zakupu DESC
            LIMIT 200;
            """
        )
        for r in rows:
            self.tree.insert(
                "", "end", values=[r["id_zakupu"], r["data_zakupu"], r["czlonek"], r["plan"], r["data_rozpoczecia"],
                                   r["data_zakonczenia"], r["cena_koncowa"], r["status"]]
            )

    def sell_pass(self):
        if self.member_var.get() not in self._member_map or self.plan_var.get() not in self._plan_map:
            messagebox.showwarning("Uwaga", "Wybierz członka i plan.")
            return

        member_id = self._member_map[self.member_var.get()]
        plan_id = self._plan_map[self.plan_var.get()]

        try:
            with self.db.tx():
                self.db.execute(Q.Q_PURCHASE_INSERT, (member_id, plan_id))

                price = self.db.fetch_one("SELECT cena_bazowa FROM Plan_karnetu WHERE id_planu=?", (plan_id,))
                if not price:
                    raise ValueError("Nie ma takiego planu.")

                self.db.execute(
                    Q.Q_PAYMENT_INSERT_LAST,
                    (float(price["cena_bazowa"]), self.method.get(), self.pay_status.get()),
                )

            self.refresh_data()
            messagebox.showinfo("OK", "Dodano zakup i płatność.")
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def search(self):
        self.refresh_data()

    # ---- CRUD ----
    def add_record(self):
        # GUI-owo: "Dodaj" = sprzedaj karnet
        self.sell_pass()

    def edit_record(self):
        vals = self.selected_row_values()
        if not vals:
            return
        purchase_id = vals[0]

        cur = self.db.fetch_one(
            """
            SELECT id_zakupu, status, cena_koncowa, data_rozpoczecia, data_zakonczenia
            FROM Zakup_karnetu
            WHERE id_zakupu=?
            """,
            (purchase_id,),
        )
        pay = self.db.fetch_one(
            """
            SELECT id_platnosci, status AS pay_status, metoda, kwota
            FROM Platnosc
            WHERE id_zakupu=?
            ORDER BY id_platnosci DESC
            LIMIT 1
            """,
            (purchase_id,),
        )

        data = simple_form(
            self,
            "Edytuj zakup/płatność",
            [
                ("status_zakupu", f"Status zakupu {PURCHASE_STATUS}"),
                ("cena_koncowa", "Cena końcowa"),
                ("data_rozpoczecia", "Data rozpoczęcia (YYYY-MM-DD)"),
                ("data_zakonczenia", "Data zakończenia (YYYY-MM-DD)"),
                ("status_platnosci", f"Status płatności {PAY_STATUS}"),
                ("metoda", f"Metoda {PAY_METHODS}"),
                ("kwota", "Kwota (liczba)"),
            ],
            initial={
                "status_zakupu": cur["status"],
                "cena_koncowa": cur["cena_koncowa"],
                "data_rozpoczecia": cur["data_rozpoczecia"],
                "data_zakonczenia": cur["data_zakonczenia"],
                "status_platnosci": "" if not pay else pay["pay_status"],
                "metoda": "" if not pay else pay["metoda"],
                "kwota": "" if not pay else pay["kwota"],
            },
        )
        if not data:
            return

        try:
            cena = float(data["cena_koncowa"])
            kwota = float(data["kwota"]) if data["kwota"] else None
        except ValueError:
            messagebox.showwarning("Uwaga", "Cena/kwota muszą być liczbami.")
            return

        try:
            with self.db.tx():
                self.db.execute(
                    """
                    UPDATE Zakup_karnetu
                    SET status=?, cena_koncowa=?, data_rozpoczecia=?, data_zakonczenia=?
                    WHERE id_zakupu=?
                    """,
                    (data["status_zakupu"], cena, data["data_rozpoczecia"], data["data_zakonczenia"], purchase_id),
                )

                if pay:
                    self.db.execute(
                        """
                        UPDATE Platnosc
                        SET status=?, metoda=?, kwota=?
                        WHERE id_platnosci=?
                        """,
                        (
                            data["status_platnosci"] or pay["pay_status"],
                            data["metoda"] or pay["metoda"],
                            kwota if kwota is not None else pay["kwota"],
                            pay["id_platnosci"],
                        ),
                    )
                else:
                    if data["status_platnosci"] and data["metoda"] and kwota is not None:
                        self.db.execute(
                            """
                            INSERT INTO Platnosc(kwota, metoda, data_platnosci, status, id_zakupu)
                            VALUES(?, ?, date('now'), ?, ?)
                            """,
                            (kwota, data["metoda"], data["status_platnosci"], purchase_id),
                        )

            self.refresh_data()
            messagebox.showinfo("OK", "Zapisano zmiany.")
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def delete_record(self):
        vals = self.selected_row_values()
        if not vals:
            return
        purchase_id = vals[0]
        if not messagebox.askyesno(
            "Potwierdź",
            f"Usunąć zakup ID={purchase_id}?\nPłatności skasują się kaskadą (ON DELETE CASCADE).",
        ):
            return
        try:
            with self.db.tx():
                self.db.execute("DELETE FROM Zakup_karnetu WHERE id_zakupu=?", (purchase_id,))
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Błąd", str(e))
