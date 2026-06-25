import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import SessionLocal, engine
from models import Base, Technician, Site, WorkOrder
from datetime import datetime, timedelta
import pandas as pd


# one time use to generate db

DATE_FORMAT = "%Y-%m-%d %H:%M"

SLA_RULES = {
    "P1": timedelta(hours=4),
    "P2": timedelta(hours=24),
    "P3": timedelta(hours=48),
    "P4": timedelta(days=5),
    "P5": timedelta(days=10),
    "P6": timedelta(days=60),
}

def calculate_due_date(created_date: str, priority: str) -> str:
    created = datetime.strptime(created_date, DATE_FORMAT)
    due = created + SLA_RULES[priority]
    return due.strftime(DATE_FORMAT)

def calculate_sla(status: str, due_date: str) -> str:
    if status == "Closed":
        return "Closed"
    now = datetime.now()
    due = datetime.strptime(due_date, DATE_FORMAT)
    if now > due:
        return "Overdue"
    if (due - now) <= timedelta(hours=24):
        return "Due Soon"
    return "On Track"

def seed_sites(db, data_dir):
    df = pd.read_csv(data_dir / "sites.csv", dtype={"site_id": str})
    count = 0

    for _, row in df.iterrows():
        existing = db.query(Site).filter(Site.site_id == row["site_id"]).first()
        if existing:
            continue

        site = Site(
            site_id=row["site_id"],
            site_name=row["site_name"],
            site_type=row["site_type"],
            city=row["city"],
            state=row["state"],
            lat=float(row["site_lat"]),
            lng=float(row["site_lng"])
        )
        db.add(site)
        count += 1

    db.commit()
    print(f"Seeded {count} sites")

def seed_technicians(db, data_dir):
    df = pd.read_csv(data_dir / "technicians.csv")
    count = 0

    for _, row in df.iterrows():
        existing = db.query(Technician).filter(
            Technician.technician_id == int(row["technician_id"])
        ).first()
        if existing:
            continue

        tech = Technician(
            technician_id=int(row["technician_id"]),
            technician=row["technician"],
            home_city=row["home_city"],
            home_state=row["home_state"],
            home_lat=float(row["home_lat"]),
            home_lng=float(row["home_lng"]),
            skills=row["skills"],
            max_miles=int(row["max_miles"]),
            max_daily_orders=int(row["max_daily_orders"]),
            available_today=row["available_today"]
        )
        db.add(tech)
        count += 1

    db.commit()
    print(f"Seeded {count} technicians")

def seed_work_orders(db, data_dir):
    df = pd.read_csv(
        data_dir / "work_orders.csv",
        dtype={"work_order_id": str, "site_id": str}
    )
    count = 0

    for _, row in df.iterrows():
        existing = db.query(WorkOrder).filter(
            WorkOrder.work_order_id == row["work_order_id"]
        ).first()
        if existing:
            continue

        due_date = calculate_due_date(row["created_date"], row["priority"])
        sla = calculate_sla(row["status"], due_date)

        work_order = WorkOrder(
            work_order_id=row["work_order_id"],
            customer=row["customer"],
            site_id=row["site_id"],
            city=row["city"],
            state=row["state"],
            issue=row["issue"],
            technician=row["technician"],
            status=row["status"],
            priority=row["priority"],
            created_date=row["created_date"],
            safety_escalation=row["safety_escalation"],
            notes=row["notes"],
            estimated_duration=float(row["estimated_hours"]),
            due_date=due_date,
            sla=sla
        )
        db.add(work_order)
        count += 1

    db.commit()
    print(f"Seeded {count} work orders")

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        data_dir = Path(__file__).parent.parent / "data"
        print("Starting seed...")
        seed_sites(db, data_dir)
        seed_technicians(db, data_dir)
        seed_work_orders(db, data_dir)
        print("Seed complete.")
    except Exception as e:
        db.rollback()
        print(f"Error during seed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()