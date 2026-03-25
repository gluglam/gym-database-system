# main.py
import tkinter as tk
from tkinter import ttk

from tabs.members import MemberTab
from tabs.employees import EmployeeTab
from tabs.equipment import EquipmentTab
from tabs.schedule import ScheduleTab
from tabs.purchases import PurchaseTab
from tabs.reports import ReportsTab

class GymApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gym – SQLite (CRUD + JasperReports)")
        self.geometry("1200x800")

        # Styling
        style = ttk.Style()
        style.theme_use("clam")

        # Tabs
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        nb.add(MemberTab(nb), text="Members")
        nb.add(EmployeeTab(nb), text="Employees")
        nb.add(ScheduleTab(nb), text="Class Schedule")
        nb.add(EquipmentTab(nb), text="Equipment")
        nb.add(PurchaseTab(nb), text="Purchases/Payments")
        nb.add(ReportsTab(nb), text="Reports")

if __name__ == "__main__":
    GymApp().mainloop()