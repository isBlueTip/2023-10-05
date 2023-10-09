from http import HTTPStatus
from typing import List

from db.models import ResourceType
from exceptions import HTTPException
from services import ResourceTypeService


class ResourceTypeController:
    def __init__(
        self,
        service: ResourceTypeService,  # todo do I need to pass a ResourceService instance here?
        path: str,  # request path
        req_body: dict = None,  # data from post if exist
        url_args: dict = None,  # data from url - filter, anything else?
    ):
        self.db_service = service
        self.path = path
        self.req_body = req_body
        self.url_args = url_args

    def list_resource_types(self) -> List[ResourceType]:
        resource_types = self.db_service.get_all_resource_types()
        return resource_types

    def get_resource_type(self, resource_type_id: int) -> ResourceType:
        resource_type = self.db_service.get_resource_type_by_id(resource_type_id)
        if not resource_type:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource type not found")
        return resource_type

    def create_resource_type(self, resource_type: ResourceType) -> ResourceType:
        created_resource_type = self.db_service.create_resource_type(resource_type)
        return created_resource_type

    def update_resource_type(self, resource_type_id: int, resource_type: ResourceType) -> ResourceType:
        updated_resource_type = self.db_service.update_resource_type(resource_type_id, resource_type)
        if not updated_resource_type:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource type not found")
        return updated_resource_type

    def delete_resource_type(self, resource_type_id: int) -> None:  # todo many?
        deleted = self.db_service.delete_resource_type(resource_type_id)
        if not deleted:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource type not found")
