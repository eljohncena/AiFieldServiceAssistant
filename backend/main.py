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
@app.get("/")
def home():
    return {"message": "Hello World"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/work-orders")
def work_orders():
    return loadWorkOrders()