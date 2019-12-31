
class ContinuousResourceAllocationSerialiser:
    @staticmethod
    def serialise(allocation) -> dict:
        return {
            'id': allocation.id,
            'resource_type': allocation.resource_type,
            'resource_id': allocation.resource_id,
            'from_infinity': allocation.from_infinity,
            'to_infinity': allocation.to_infinity,
            'from_datetime': (
                allocation.from_datetime.strftime("%Y-%m-%dT%H:%M:%S")
                if allocation.from_datetime
                else None
            ),
            'to_datetime': (
                allocation.to_datetime.strftime("%Y-%m-%dT%H:%M:%S")
                if allocation.to_datetime
                else None
            ),
            'allocation_type': allocation.allocation_type,
            'description': allocation.description,
            'dump': allocation.dump
        }
