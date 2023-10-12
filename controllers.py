import http
from abc import ABC, abstractmethod
from typing import List

import exceptions
from db.db_adapter import DBAdapter
from db.models import Resource, ResourceType
from exceptions import HTTPException


class BaseDBController(ABC):
    def __init__(
        self,
        url,
        request_json: dict | None = None,  # data from post if exist
        url_params: dict | None = None,  # data from url - filter, anything else?
    ):
        self.url = url
        self.request_json = request_json
        self.url_params = url_params

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def retrieve(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    def url_as_list(self):
        return self.url.path.strip("/").split("/")


class ResourceTypeController(BaseDBController):
    def create(self) -> List[ResourceType] | None:
        url = self.url_as_list()
        if len(url) > 1:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "can't post to specific id")

        # validate request data
        if not self.request_json:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "request body contains no data")

        if (name := self.request_json.get("name")) is None:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "you have to specify name")
        if (max_speed := self.request_json.get("max_speed")) is None:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "you have to specify max_speed")

        # create ResourceType object and send its data to db adapter
        resource_type = ResourceType(name=name, max_speed=max_speed)

        adapter = DBAdapter()
        result = adapter.create(resource_type, "resource_type")

        return [result]

    def retrieve(self) -> List[ResourceType]:
        url = self.url_as_list()

        # parse resource_type id
        resource_type_id = None
        if len(url) > 1:
            resource_type_id = url[1]
            if not resource_type_id.isnumeric():  # not numeric argument
                raise exceptions.NotFound(detail=f"resource_type id has to be int")
            resource_type_id = int(resource_type_id)

        # create filtering data
        filtering_data = {}

        adapter = DBAdapter()
        resource_types = adapter.retrieve(ResourceType, "resource_type", resource_type_id, filtering_data)

        return resource_types

    def update(self) -> List[ResourceType]:
        url = self.url_as_list()

        # parse resource_type id
        if len(url) > 1:
            resource_type_id = url[1]
            if not resource_type_id.isnumeric():  # not numeric argument
                raise exceptions.NotFound(detail=f"{resource_type_id} not found")
            resource_type_id = int(resource_type_id)
        else:
            raise exceptions.NotFound(detail=f"resource_type id not specified")

        # validate request data
        if not self.request_json:
            raise exceptions.BadRequest("request body contains no data")

        name = self.request_json.get("name")
        max_speed = self.request_json.get("max_speed")

        if all((name is None, max_speed is None)):
            raise exceptions.BadRequest("at least one attribute to change have to be specified")

        # create filtering data
        filtering_data = {}

        adapter = DBAdapter()

        # retrieve existing ResourceType object
        resource_type = adapter.retrieve(ResourceType, "resource_type", resource_type_id, filtering_data)[0]

        # update and send object data to db connection
        if name is not None:
            resource_type.name = name
        if max_speed is not None:
            resource_type.max_speed = max_speed

        adapter.update(resource_type, "resource_type", resource_type_id)

        return [resource_type]

    def delete(self) -> None:
        url = self.url_as_list()
        if len(url) > 1:
            raise exceptions.BadRequest("specify id for deletion as in '?id=x,y'")

        # parse ids
        raw_ids = self.url_params.get("id")
        if not raw_ids:
            raise exceptions.BadRequest(detail="specify id for deletion as in '?id=x,y'")
        resource_type_ids = raw_ids[0].split(",")

        # validate ids
        try:
            resource_type_ids = tuple(map(int, resource_type_ids))
        except ValueError:
            raise exceptions.BadRequest(detail=f"wrong id parameters, awaiting ints")

        adapter = DBAdapter()

        adapter.delete("resource_type", resource_type_ids)
        return


class ResourceController(BaseDBController):
    def create(self) -> List[Resource] | None:
        url = self.url_as_list()
        if len(url) > 1:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "can't post to specific id")

        # validate request data
        if not self.request_json:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "request body contains no data")

        if (name := self.request_json.get("name")) is None:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "you have to specify name")
        if (resource_type_id := self.request_json.get("resource_type_id")) is None:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "you have to specify resource_type_id")
        if (current_speed := self.request_json.get("current_speed")) is None:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "you have to specify current_speed")

        # create Resource object and send its data to db adapter
        resource = Resource(name=name, resource_type_id=resource_type_id, current_speed=current_speed)

        adapter = DBAdapter()
        result = adapter.create(resource, "resource")

        return [result]

    def retrieve(self) -> List[Resource]:
        url = self.url_as_list()

        # parse resource id
        resource_id = None
        if len(url) > 1:
            resource_id = url[-1]
            if not resource_id.isnumeric():  # not numeric argument
                raise exceptions.NotFound(detail=f"resource id has to be int")
            resource_id = int(resource_id)

        # parse filtering params
        raw_type_ids = self.url_params.get("type")

        # create filtering data
        filtering_data = {}
        if raw_type_ids:
            type_ids = raw_type_ids[0].split(",")
            try:
                type_ids = tuple(map(int, type_ids))
            except ValueError:
                raise exceptions.BadRequest(detail=f"wrong type url parameters")
            else:
                filtering_data["type_id"] = type_ids

        adapter = DBAdapter()
        resources = adapter.retrieve(Resource, "resource", resource_id, filtering_data)

        return resources

    def update(self) -> List[Resource]:
        url = self.url_as_list()

        # parse resource id
        if len(url) > 1:
            resource_id = url[1]
            if not resource_id.isnumeric():  # not numeric argument
                raise exceptions.NotFound(detail=f"{resource_id} not found")
            resource_id = int(resource_id)
        else:
            raise exceptions.NotFound(detail=f"resource id not specified")

        # validate request data
        if not self.request_json:
            raise exceptions.BadRequest("request body contains no data")

        name = self.request_json.get("name")
        resource_type_id = self.request_json.get("resource_type_id")
        current_speed = self.request_json.get("current_speed")

        if all((name is None, resource_type_id is None, current_speed is None)):
            raise exceptions.BadRequest("at least one attribute to change have to be specified")

        # create filtering data
        filtering_data = {}

        adapter = DBAdapter()

        # retrieve existing Resource object
        resource = adapter.retrieve(Resource, "resource", resource_id, filtering_data)[0]

        # update and send object data to db connection
        if name is not None:
            resource.name = name
        if resource_type_id is not None:
            resource.resource_type_id = resource_type_id
        if current_speed is not None:
            resource.current_speed = current_speed

        adapter.update(resource, "resource", resource_id)

        return [resource]

    def delete(self) -> None:
        url = self.url_as_list()
        if len(url) > 1:
            raise exceptions.BadRequest("specify id for deletion as in '?id=x,y'")

        # parse ids
        raw_ids = self.url_params.get("id")
        if not raw_ids:
            raise exceptions.BadRequest(detail="specify id for deletion as in '?id=x,y'")
        resource_ids = raw_ids[0].split(",")

        # validate ids
        try:
            resource_ids = tuple(map(int, resource_ids))
        except ValueError:
            raise exceptions.BadRequest(detail=f"wrong id parameters, awaiting ints")

        adapter = DBAdapter()

        adapter.delete("resource", resource_ids)
        return
