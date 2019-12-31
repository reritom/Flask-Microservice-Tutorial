from flask import Blueprint, jsonify, request, abort
from daos.continuous_resource_dao import ContinuousResourceDao
from serialisers.continuous_resource_serialiser import ContinuousResourceSerialiser
from serialisers.continuous_resource_allocation_serialiser import ContinuousResourceAllocationSerialiser
from common.tools import datetime_from_string
from blueprints.tools import AllocationError
import json
import logging

logger = logging.getLogger(__name__)

def create_blueprint(blueprint_name: str, resource_type: str, resource_prefix: str):
    """
    blueprint_name: name of the blueprint, used by Flask for routing
    resource_type: name of the specific type of interval resource, such as boy bay or payload bay
    resource_prefix: the plural resource to be used in the api endpoint, such as bot_bay, resulting in "/bot_bays"
    """
    blueprint = Blueprint(blueprint_name, __name__)

    @blueprint.route(f'/{resource_prefix}', methods=["POST"])
    def create_resource():
        logger.info("Creating resource")
        resource = ContinuousResourceDao.create_resource(resource_type=resource_type, name=request.get_json(force=True)['name'])
        return ContinuousResourceSerialiser.serialise(resource), 201

    @blueprint.route(f'/{resource_prefix}', methods=["GET"])
    def get_resources():
        """
        Get all the resources sans allocations
        """
        logger.info("Getting resources")
        return jsonify([
            ContinuousResourceSerialiser.serialise(resource)
            for resource in ContinuousResourceDao.get_resources(resource_type=resource_type)
        ]), 200

    @blueprint.route(f'/{resource_prefix}/<resource_id>', methods=["GET"])
    def get_resource(resource_id):
        """
        Get the details of a specific resource
        """
        logger.info(f"Getting resource {resource_id}")
        resource = ContinuousResourceDao.get_resource_by_id(resource_type=resource_type, resource_id=resource_id)
        return jsonify(ContinuousResourceSerialiser.serialise(resource)), 200

    @blueprint.route(f'/{resource_prefix}/<resource_id>', methods=["PATCH"])
    def modify_resource(resource_id):
        pass

    @blueprint.route(f'/{resource_prefix}/<resource_id>/allocations', methods=["GET"])
    def get_resource_allocations(resource_id):
        """
        Get all the allocations for a specific resource
        """
        allocations = ContinuousResourceDao.get_resource_allocations(resource_type=resource_type, resource_id=resource_id)
        return jsonify([ContinuousResourceAllocationSerialiser.serialise(allocation) for allocation in allocations]), 200

    @blueprint.route(f'/{resource_prefix}/any/allocations', methods=["POST"])
    def create_any_resource_allocation():
        """
        Create an allocation for whichever resource is first available for the given allocation period
        """
        resources = ContinuousResourceDao.get_resources(resource_type=resource_type)

        data = request.get_json(force=True)

        from_infinity = data.get('from_infinity', False)
        from_datetime = (
            datetime_from_string(data['from_datetime'])
            if 'from_datetime' in data
            else None
        )

        to_infinity = data.get('to_infinity', False)
        to_datetime = (
            datetime_from_string(data['to_datetime'])
            if 'to_datetime' in data
            else None
        )

        for resource in resources:
            logger.debug(f"Looking at resource {resource.id}")

            # Get the existing allocations
            existing_allocations = [allocation for allocation in resource.allocations]
            existing_allocations.sort(key=lambda allocation: allocation.to_datetime if allocation.to_datetime else allocation.from_datetime)
            logger.debug(f"There are {len(existing_allocations)} existing allocations")

            if to_infinity and from_infinity and existing_allocations:
                logger.debug(f"Skipping, there are existing allocations and an infinite request")
                continue

            # Determine if they are attempting to create an overlap
            try:
                for allocation in existing_allocations:
                    if allocation.from_infinity and allocation.to_infinity:
                        logger.debug("Skipping, an infinite allocation exists")
                        raise AllocationError()
                    elif allocation.from_infinity:
                        if (
                            (to_datetime and to_datetime < allocation.to_datetime)
                            or
                            (from_datetime and from_datetime < allocation.to_datetime)
                            or
                            from_infinity
                        ):
                            raise AllocationError()
                    elif allocation.to_infinity:
                        if (
                            (to_datetime and to_datetime > allocation.from_datetime)
                            or
                            (from_datetime > allocation.from_datetime)
                            or
                            to_infinity
                        ):
                            raise AllocationError()
                    else:
                        logger.debug("Looking at normal cases")
                        if (
                            from_datetime
                            and
                            from_datetime > allocation.from_datetime
                            and
                            from_datetime < allocation.to_datetime
                        ):
                            logger.debug("From datetime overlaps with an existing allocation")
                            raise AllocationError()
                        if (
                            to_datetime
                            and
                            to_datetime > allocation.from_datetime
                            and
                            to_datetime < allocation.to_datetime
                        ):
                            logger.debug("To datetime overlaps with an existing allocation")
                            raise AllocationError()
            except AllocationError:
                # Lets look at the next resource instead
                logger.debug("This resource is already allocated, lets look at the next")
                continue

            logger.debug(f"Creating allocation for resource {resource.id}")
            allocation = ContinuousResourceDao.create_resource_allocation(
                resource_type=resource_type,
                resource_id=resource.id,
                from_datetime=from_datetime,
                to_datetime=to_datetime,
                from_infinity=from_infinity,
                to_infinity=to_infinity,
                allocation_type=data['allocation_type'],
                description=data.get('description'),
                json_dump=json.dumps(data.get('dump', {}))
            )
            return jsonify(ContinuousResourceAllocationSerialiser.serialise(allocation)), 201
        else:
            # None of the resources were able to be allocated
            logger.debug("No more resources to look at, unable to create allocation")
            return abort(406)

    @blueprint.route(f'/{resource_prefix}/<resource_id>/allocations', methods=["POST"])
    def create_resource_allocation(resource_id):
        """
        Create an allocation for a specific resource
        """
        resource = ContinuousResourceDao.get_resource_by_id(resource_type=resource_type, resource_id=resource_id)

        if not resource:
            logger.debug("No resource found")
            abort(404)

        data = request.get_json(force=True)

        from_infinity = data.get('from_infinity', False)
        from_datetime = (
            datetime_from_string(data['from_datetime'])
            if 'from_datetime' in data
            else None
        )

        to_infinity = data.get('to_infinity', False)
        to_datetime = (
            datetime_from_string(data['to_datetime'])
            if 'to_datetime' in data
            else None
        )

        # Get the existing allocations
        existing_allocations = [allocation for allocation in resource.allocations]
        existing_allocations.sort(key=lambda allocation: allocation.to_datetime if allocation.to_datetime else allocation.from_datetime)

        if to_infinity and from_infinity and existing_allocations:
            logger.debug("Aborting, there are existing allocations and an infinite request")
            abort(406)

        # Determine if they are attempting to create an overlap
        for allocation in existing_allocations:
            if allocation.from_infinity and allocation.to_infinity:
                logger.debug("Aborting, an infinite allocation exists")
                abort(406)
            elif allocation.from_infinity:
                if (
                    (to_datetime and to_datetime < allocation.to_datetime)
                    or
                    (from_datetime and from_datetime < allocation.to_datetime)
                    or
                    from_infinity
                ):
                    abort(406)
            elif allocation.to_infinity:
                if (
                    (to_datetime and to_datetime > allocation.from_datetime)
                    or
                    (from_datetime > allocation.from_datetime)
                    or
                    to_infinity
                ):
                    abort(406)
            else:
                logger.debug("Looking at normal cases")
                if (
                    from_datetime
                    and
                    from_datetime > allocation.from_datetime
                    and
                    from_datetime < allocation.to_datetime
                ):
                    logger.debug("From datetime overlaps with an existing allocation")
                    abort(406)
                if (
                    to_datetime
                    and
                    to_datetime > allocation.from_datetime
                    and
                    to_datetime < allocation.to_datetime
                ):
                    logger.debug("To datetime overlaps with an existing allocation")
                    abort(406)

        allocation = ContinuousResourceDao.create_resource_allocation(
            resource_type=resource_type,
            resource_id=resource_id,
            from_datetime=from_datetime,
            to_datetime=to_datetime,
            from_infinity=from_infinity,
            to_infinity=to_infinity,
            allocation_type=data['allocation_type'],
            description=data.get('description'),
            json_dump=json.dumps(data.get('dump', {}))
        )
        return jsonify(ContinuousResourceAllocationSerialiser.serialise(allocation)), 201


    @blueprint.route(f'/{resource_prefix}/<resource_id>/allocations/<allocation_id>', methods=["GET"])
    def get_resource_allocation(resource_id, allocation_id):
        """
        Get a specific allocation by allocation id
        """
        allocation = ContinuousResourceDao.get_resource_allocation_by_id(resource_type=resource_type, allocation_id=allocation_id)
        return ContinuousResourceAllocationSerialiser.serialise(allocation), 200

    @blueprint.route(f'/{resource_prefix}/all/allocations/<allocation_id>', methods=["DELETE"])
    @blueprint.route(f'/{resource_prefix}/<resource_id>/allocations/<allocation_id>', methods=["DELETE"])
    def delete_resource_allocation(resource_id=None, allocation_id=None):
        """
        Delete any allocation with the provided allocation id, disregarding the resource id
        """
        ContinuousResourceDao.delete_resource_allocation_by_id(resource_type=resource_type, allocation_id=allocation_id)
        return jsonify({}), 200

    return blueprint
