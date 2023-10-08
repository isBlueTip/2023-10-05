from http import HTTPStatus
from typing import List

from db.models import Resource
from exceptions import HTTPException
from services.resource_service import ResourceService


class ResourceController:
    def __init__(self, resource_service: ResourceService):
        self.resource_service = resource_service

    def get_resources(self) -> List[Resource]:
        resources = self.resource_service.list_resources()
        return resources

    def get_resource(self, resource_id: int) -> Resource:
        resource = self.resource_service.get_resource(resource_id)
        if not resource:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource not found")
        return resource

    def create_resource(self, resource: Resource) -> Resource:
        created_resource = self.resource_service.create_resource(resource)
        return created_resource

    def update_resource(self, resource_id: int, resource: Resource) -> Resource:
        updated_resource = self.resource_service.update_resource(resource_id, resource)
        if not updated_resource:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource not found")
        return updated_resource

    def delete_resource(self, resource_id: int) -> None:
        deleted = self.resource_service.delete_resource(resource_id)
        if not deleted:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource not found")
