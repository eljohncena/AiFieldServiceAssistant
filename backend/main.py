from database import engine, get_db
from models import Base, WorkOrder, Technician, Site, Assignment
from sqlalchemy.orm import Session
from fastapi import FastAPI, Query, Depends, HTTPException
from schemas import AssignmentCreate

Base.metadata.create_all(bind=engine)
app = FastAPI()

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
    db: Session = Depends(get_db)

):
    query = db.query(WorkOrder)
    if status:
        query = query.filter(WorkOrder.status.ilike(f"%{status}%"))
    if priority:
        query = query.filter(WorkOrder.priority.ilike(f"%{priority}%"))
    if city:
        query = query.filter(WorkOrder.city.ilike(f"%{city}%"))
    if state:
        query = query.filter(WorkOrder.state.ilike(f"%{state}%"))
    if technician:
        query = query.filter(WorkOrder.technician.ilike(f"%{technician}%"))
    if sla:
        query = query.filter(WorkOrder.sla.ilike(f"%{sla}%"))
    if safety_escalation:
        query = query.filter(WorkOrder.safety_escalation.ilike(f"%{safety_escalation}%"))
    if site_id:
        query = query.filter(WorkOrder.site_id.ilike(f"%{site_id}%"))
    return query.all()


# End point to display the dashboard summary.
@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    all_orders = db.query(WorkOrder).all()

    return {
        "total_work_orders": len(all_orders),
        "open_work_orders": sum(1 for wo in all_orders if wo.status == "Open"),
        "in_progress_work_orders": sum(1 for wo in all_orders if wo.status == "In Progress"),
        "closed_work_orders": sum(1 for wo in all_orders if wo.status == "Closed"),
        "overdue_work_orders": sum(1 for wo in all_orders if wo.sla == "Overdue"),
        "due_soon_work_orders": sum(1 for wo in all_orders if wo.sla == "Due Soon"),
        "safety_escalation": sum(1 for wo in all_orders if wo.safety_escalation == "Yes"),
        "p1_orders": sum(1 for wo in all_orders if wo.priority == "P1"),
    }

# End point to display a specific work order.
@app.get("/work-orders/{work_order_id}")
def get_work_order(work_order_id: str, db: Session = Depends(get_db)):
    work_order = db.query(WorkOrder).filter(WorkOrder.work_order_id == work_order_id).first()

    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")

    return work_order

# End point to display all technicians.
@app.get("/technicians")
def get_technicians(db: Session = Depends(get_db)):
    return db.query(Technician).all()

#Display a specific technician.
@app.get("/technicians/{technician_id}")
def get_technician(technician_id: int, db: Session = Depends(get_db)):
    tech = db.query(Technician).filter(Technician.technician_id == technician_id).first()

    if not tech:
        raise HTTPException(status_code=404, detail="Technician not found")

    return tech

# Test endpoint for database
@app.get("/db-test")
def test_db(db: Session = Depends(get_db)):
    return {
        "work_orders": db.query(WorkOrder).count(),
        "technicians": db.query(Technician).count(),
        "sites": db.query(Site).count()
    }

@app.post("/assignments")
def create_assignment(assignment: AssignmentCreate, db: Session = Depends(get_db)):

    # Checks if technician exists
    tech = db.query(Technician).filter(Technician.technician_id == assignment.technician_id).first()

    if not tech:
        raise HTTPException(status_code=404, detail="Technician not found")

    # Checks if site exists
    site = db.query(Site).filter(Site.site_id == assignment.site_id).first()

    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    site_conflict = db.query(Assignment).filter(Assignment.site_id == assignment.site_id, Assignment.scheduled_date == assignment.scheduled_date).first()

    # Checks if site is already assigned to another technician
    if site_conflict:
        raise HTTPException(status_code=400, detail=f"Site {assignment.site_id} is already assigned to {Assignment.technician} on {assignment.scheduled_date}")

    existing_assignments = db.query(Assignment).filter(Assignment.technician_id == assignment.technician_id, Assignment.scheduled_date == assignment.scheduled_date).all()

    # New work order duration
    committed_hours = 0
    for existing_assignment in existing_assignments:
        wo = db.query(WorkOrder).filter(WorkOrder.work_order_id == existing_assignment.work_order_id).first()
        if wo:
            committed_hours += wo.estimated_duration

    new_work_order = db.query(WorkOrder).filter(WorkOrder.work_order_id == assignment.work_order_id).first()

    if not new_work_order:
        raise HTTPException(status_code=404, detail="Work order not found")


    # Check if the new work order will put the technician over the 8 hour limit
    projected_hours = committed_hours + new_work_order.estimated_duration

    if projected_hours > 8:
        raise HTTPException(status_code=400, detail=f"Work order would put {tech.technician} over the project limit of 8 hours")

    # If passes all checks
    new_assignment = Assignment(
        technician_id = assignment.technician_id,
        site_id = assignment.site_id,
        work_order_id = assignment.work_order_id,
        scheduled_date = assignment.scheduled_date
    )

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    return {
        "message": "Assignment created successfully",
        "assignment": new_assignment.id,
        "technician": tech.technician,
        "site": site.site_name,
        "scheduled_date": new_assignment.scheduled_date,
        "commited_hours": round(committed_hours, 2),

    }

# Get assignment endpoint
@app.get("/assignments")
def get_assignment(scheduled_date: str | None = Query(default=None),
                   technician_id: int | None = Query(default=None),
                    site_id: str | None = Query(default=None),
                    db: Session = Depends(get_db)):

    query = db.query(Assignment)

    if scheduled_date:
        query = query.filter(Assignment.scheduled_date == scheduled_date)
    if technician_id:
        query = query.filter(Assignment.technician_id == technician_id)
    if site_id:
        query = query.filter(Assignment.site_id == site_id)
    return query.all()