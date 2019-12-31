from database import db
import datetime

class ContinuousResourceAllocation(db.Model):
    __tablename__ = "continuous_resource_allocations"

    # Ids
    id = db.Column(db.String(36), primary_key=True, unique=True)

    # Parents
    resource_id = db.Column(db.ForeignKey('continuous_resources.id'))
    resource = db.relationship('ContinuousResource', foreign_keys=resource_id)

    # Attributes
    resource_type = db.Column(db.String(36), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    from_infinity = db.Column(db.Boolean, default=False)
    to_infinity = db.Column(db.Boolean, default=False)
    from_datetime = db.Column(db.DateTime, nullable=True)
    to_datetime = db.Column(db.DateTime, nullable=True)
    allocation_type = db.Column(db.String(20))
    description = db.Column(db.String(100), nullable=True)
    json_dump = db.Column(db.String(200), nullable=True)

    @property
    def dump(self) -> dict:
        try:
            return json.loads(self.json_dump)
        except:
            return {}
