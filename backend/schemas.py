from pydantic import BaseModel

class AssignmentCreate(BaseModel):
    technician_id: int
    site_id: str
    work_order_id: str
    scheduled_date: str
