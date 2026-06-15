from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello World"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/work-orders")
def work_orders():
    return {"message": "Hello Work Orders"}