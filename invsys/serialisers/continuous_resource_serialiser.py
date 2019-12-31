
class ContinuousResourceSerialiser:
    @staticmethod
    def serialise(resource) -> dict:
        return {
            'id': resource.id,
            'name': resource.name,
            'resource_type': resource.resource_type,
            'created': resource.created.strftime("%Y-%m-%dT%H:%M:%S")
        }
