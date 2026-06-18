from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Technician(Base):
    __tablename__ = "technicians"
    id = Column(Integer, primary_key=True, index=True)
    technician = Column(String, nullable = False)
    home_city = Column(String)
    home_state = Column(String)
    home_lat = Column(Float)
    home_long = Column(Float)

    assignments = relationship("Assignment", back_populates="technician")


class Site(Base):
    __tablename__ = "sites"
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(String, unique=True, index=True)
    site_name = Column(String)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    lat = Column(Float)
    long = Column(Float)

    assignments = relationship("Assignment", back_populates="site")

class WorkOrder(Base):
    __tablename__ = "work_orders"
    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(String, unique=True, index=True)
    site_id = Column(String, ForeignKey("sites.site_id"))
    customer = Column(String)
    due_date = Column(String)
    city = Column(String)
    state = Column(String)
    issue = Column(String)
    technician = Column(String)
    status = Column(String)
    priority = Column(String)
    sla = Column(String)
    created_date = Column(String)
    notes = Column(String)
    safety_escalation = Column(String)
    estimated_hours = Column(Float)

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    technician_id = Column(String, ForeignKey("technicians.id"))
    site_id = Column(String, ForeignKey("sites.id"))
    work_order_id = Column(String, ForeignKey("work_orders.id"))
    status = Column(String, default="Scheduled")
    scheduled_date = Column(String)

    technician = relationship("Technician", back_populates="assignments")
    site = relationship("Site", back_populates="assignments")

class RouteCache(Base):
    __tablename__ = "route_cache"
    id = Column(Integer, primary_key=True, index=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    driving_miles = Column(Float)
    driving_minutes = Column(Float)
    cached_at = Column(String)




