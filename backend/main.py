from fastapi import FastAPI
from pathlib import Path
import pandas as pd
app = FastAPI()

dataFile = Path(__file__).parent.parent / "data" / "work_orders.csv"

def loadWorkOrders() -> list[dict]:
    df = pd.read_csv(dataFile)
    workOrders = df.to_dict(orient="records")

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