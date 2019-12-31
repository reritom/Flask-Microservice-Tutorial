from database import db
import datetime

class ContinuousResource(db.Model):
    __tablename__ = "continuous_resources"

    id = db.Column(db.String(36), primary_key=True, unique=True)
    name = db.Column(db.String(36), primary_key=True, unique=True) # Eg Lander1
    resource_type = db.Column(db.String(36), primary_key=True) # Launcher/Lander/Multi
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    # Children
    allocations = db.relationship("ContinuousResourceAllocation", back_populates="resource", lazy=True)
