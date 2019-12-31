from database import db
from typing import List
from models.continuous_resource import ContinuousResource
from models.continuous_resource_allocation import ContinuousResourceAllocation
import uuid

class ContinuousResourceDao:
    @staticmethod
    def create_resource(resource_type, name) -> ContinuousResource:
        resource = ContinuousResource(
            id=str(uuid.uuid4()),
            resource_type=resource_type,
            name=name
        )
        db.session.add(resource)
        db.session.commit()
        return resource

    @staticmethod
    def get_resources(resource_type) -> List[ContinuousResource]:
        return ContinuousResource.query.filter_by(resource_type=resource_type)

    @staticmethod
    def get_resource_by_id(resource_type, resource_id) -> ContinuousResource:
        return ContinuousResource.query.filter(ContinuousResource.id == resource_id).first()

    @staticmethod
    def create_resource_allocation(resource_type, resource_id, **kwargs) -> ContinuousResourceAllocation:
        allocation = ContinuousResourceAllocation(
            id=str(uuid.uuid4()),
            resource_type=resource_type,
            resource_id=resource_id,
            **kwargs
        )
        db.session.add(allocation)
        db.session.commit()
        return allocation

    @staticmethod
    def get_resource_allocations(resource_type, resource_id) -> List[ContinuousResourceAllocation]:
        resource = ContinuousResource.query.filter(ContinuousResource.id == resource_id).first()
        return resource.allocations

    @staticmethod
    def get_resource_allocation_by_id(resource_type, allocation_id) -> ContinuousResourceAllocation:
        return ContinuousResourceAllocation.query.filter(ContinuousResourceAllocation.id == allocation_id).first()

    @staticmethod
    def delete_resource_allocation_by_id(resource_type, allocation_id):
        ContinuousResourceAllocation.query.filter(ContinuousResourceAllocation.id == allocation_id).delete()
        db.session.commit()
