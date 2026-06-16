from fastapi import FastAPI
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
app = FastAPI()

dataFile = Path(__file__).parent.parent / "data" / "work_orders.csv"
dateFormat = "%Y-%m-%d %H:%M"

slaRules = {
    "P1": timedelta(hours=4),
    "P2": timedelta(hours=24),
    "P3": timedelta(hours=48),
    "P4": timedelta(days=5),
    "P5": timedelta(days=10),
    "P6": timedelta(days=60),
    }

def calculateDueDate(created_date: str, priority: str) ->str:
    created = datetime.strptime(created_date, dateFormat)
    slaDuration = slaRules[priority]
    dueDate = created + slaDuration
    return dueDate.strftime(dateFormat)

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

def loadWorkOrders() -> list[dict]:
    df = pd.read_csv(dataFile)
    workOrders = df.to_dict(orient="records")

    for workOrder in workOrders:
        dueDate = calculateDueDate(workOrder["created_date"], workOrder["priority"])
        workOrder["due_date"] = dueDate
        workOrder["sla"] = calculateSla(workOrder["status"], dueDate)

    return workOrders

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

@app.get("/")
def home():
    return {"message": "Hello World"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/work-orders")
def work_orders():
    return loadWorkOrders()

@app.get("/dashboard")
def dashboard():
    return buildDashboardSummary()