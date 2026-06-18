from fastapi import FastAPI, Query
from pathlib import Path
from datetime import datetime, timedelta

from database import engine
from models import Base

import pandas as pd

Base.metadata.create_all(bind=engine)
app = FastAPI()


dataFile = Path(__file__).parent.parent / "data" / "work_orders.csv"
technicianFile = Path(__file__).parent.parent / "data" / "technicians.csv"

dateFormat = "%Y-%m-%d %H:%M"

# SLA rules for different priorities.
slaRules = {
    "P1": timedelta(hours=4),
    "P2": timedelta(hours=24),
    "P3": timedelta(hours=48),
    "P4": timedelta(days=5),
    "P5": timedelta(days=10),
    "P6": timedelta(days=60),
    }

# Function to calculate the due date based on the priority.
def calculateDueDate(created_date: str, priority: str) ->str:
    created = datetime.strptime(created_date, dateFormat)
    slaDuration = slaRules[priority]
    dueDate = created + slaDuration
    return dueDate.strftime(dateFormat)

# Function to calculate the SLA status.
def calculateSla(status: str, dueDate: str) -> str:
    if status == "Closed":
        return "Closed"
    now = datetime.now()
    due = datetime.strptime(dueDate, dateFormat)
    timeUntilDue = due - now

    if now > due:
        return "Overdue"

    if timeUntilDue <= timedelta(hours=24):
        return "Due Soon"
    return "On Track"

# Function to load all work orders from the csv file. Force pandas to read work_order_id and site_id as str
def loadWorkOrders() -> list[dict]:
    df = pd.read_csv(dataFile, dtype={"work_order_id": str, "site_id": str})
    workOrders = df.to_dict(orient="records")

    for workOrder in workOrders:
        dueDate = calculateDueDate(workOrder["created_date"], workOrder["priority"])
        workOrder["due_date"] = dueDate
        workOrder["sla"] = calculateSla(workOrder["status"], dueDate)

    return workOrders

# Function to build the dashboard summary.
def buildDashboardSummary() -> dict:
    work_orders = loadWorkOrders()
    totalWorkOrders = len(work_orders)
    openWorkOrders = 0
    inProgressWorkOrders = 0
    closedWorkOrders = 0
    overdueWorkOrders = 0
    dueSoonWorkOrders = 0
    safetyEscalation = 0
    p1Orders = 0

    for workOrder in work_orders:
        if workOrder["status"] == "Open":
            openWorkOrders += 1
        if workOrder["status"] == "In Progress":
            inProgressWorkOrders += 1
        if workOrder["status"] == "Closed":
            closedWorkOrders += 1
        if workOrder["sla"] == "Overdue":
            overdueWorkOrders += 1
        if workOrder["sla"] == "Due Soon":
            dueSoonWorkOrders += 1
        if workOrder["priority"] == "P1":
            p1Orders += 1
        if workOrder["safety_escalation"] == "Yes":
            safetyEscalation += 1

    return {

        "total_work_orders": totalWorkOrders,
        "open_work_orders": openWorkOrders,
        "in_progress_work_orders": inProgressWorkOrders,
        "closed_work_orders": closedWorkOrders,
        "overdue_work_orders": overdueWorkOrders,
        "due_soon_work_orders": dueSoonWorkOrders,
        "safety_escalation": safetyEscalation,
        "p1_orders": p1Orders,

    }

# End point to display the home page.
@app.get("/")
def home():
    return {"message": "Hello World"}

# End point to check the health of the application.
@app.get("/health")
def health_check():
    return {"status": "ok"}


# End point to display all work orders.
@app.get("/work-orders")

# Query parameters to filter the work orders.
def work_orders(
    status: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    city: str | None = Query(default=None),
    state: str | None = Query(default=None),
    technician: str | None = Query(default=None),
    sla: str | None = Query(default=None),
    safety_escalation: str | None = Query(default=None),
    site_id: str | None = Query(default=None),
):
    workOrders = loadWorkOrders()  #loads all work orders from csv, then filters. Will switch to a database later.

    # Filters will only run if the user provides a value. e.g., /work-orders?status=Open&priority=P1&location=Raleigh
    if status:
        workOrders = [workOrder for workOrder in workOrders if workOrder["status"].lower() == status.lower()]

    if priority:
        workOrders = [workOrder for workOrder in workOrders if workOrder["priority"].lower() == priority.lower()]

    # Filter by technician, city and state with partial match
    if city:
        workOrders = [workOrder for workOrder in workOrders if city.lower() in workOrder["city"].lower()]
    if state:
        workOrders = [workOrder for workOrder in workOrders if state.lower() in workOrder["state"].lower()]

    if technician:
        workOrders = [workOrder for workOrder in workOrders if technician.lower() in workOrder["technician"].lower()]

    if sla:
        workOrders = [workOrder for workOrder in workOrders if workOrder["sla"].lower() == sla.lower()]

    if safety_escalation:
        workOrders = [workOrder for workOrder in workOrders if workOrder["safety_escalation"].lower() == safety_escalation.lower()]

    if site_id:
        workOrders = [workOrder for workOrder in workOrders if site_id.strip().lower() in str(workOrder["site_id"]).strip().lower()]

    return workOrders

# End point to display the dashboard summary.
@app.get("/dashboard")
def dashboard():
    return buildDashboardSummary()

# End point to display a specific work order.
@app.get("/work-orders/{work_order_id}")
def get_work_order(work_order_id: str):
    work_orders = loadWorkOrders()

    for work_order in work_orders:
        if work_order["work_order_id"].lower() == work_order_id.lower():
            return work_order

    return {"error": "Work order not found"}


# End point to display all technicians.
@app.get("/technicians")
def get_technicians():
    df = pd.read_csv(technicianFile)
    return df.to_dict(orient="records")

#Display a specific technician.
@app.get("/technicians/{technician_id}")
def get_technician(technician_id: int):
    technicians = get_technicians()

    for technician in technicians:
        if technician["technician_id"] == technician_id:
            return technician
    return {"error": "Technician not found"}
