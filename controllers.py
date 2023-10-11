import dataclasses
import http
from abc import ABC, abstractmethod
from typing import List

from ipdb import set_trace

import exceptions
from config import Config
from db.db_access import DatabaseAccess
from db.db_adapter import DBAdapter
from db.models import Resource, ResourceType
from exceptions import HTTPException

db = DatabaseAccess(
    db_name=Config.DB_NAME,
    username=Config.DB_USERNAME,
    password=Config.DB_PASSWORD,
    host=Config.DB_HOST,
    # host='db',
    port=Config.DB_PORT,
)

# TODO CONTROLLERS PARSE DATA TO DATACLASS AND CALL SERVICE
# TODO SERVICE SENDS DATACLASS DATA TO DB AND CALL REQUIRED METHOD OF DB


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

        # TODO move closer to DB
        # check if db tables exist init and populate if not
        self.init_tables()

    @staticmethod
    def init_tables() -> None:
        with db.connect() as conn:
            cur = conn.cursor()
            query = """
            SELECT 
              EXISTS (
                SELECT 
                FROM 
                  information_schema.tables 
                WHERE 
                  table_name = 'resource_type'
              );
               """
            cur.execute(query)  # check if tables in db already exist
            exists = cur.fetchone()[0]
            cur.close()
        if not exists:  # create tables if not exist
            db.create_tables()
            db.insert_fixtures()

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
    def create(self) -> ResourceType | None:
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

        return result

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

    def update(self) -> ResourceType:
        url = self.url_as_list()

        # parse resource id
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

        # retrieve existing ResourceType object
        db_data = db.retrieve_records("resource_type", resource_type_id, None)
        if not db_data:
            raise exceptions.NotFound(detail=f"object with id = {resource_type_id} not found")

        # update and send object data to db connection
        obj = ResourceType(name=db_data[0][1], max_speed=db_data[0][2])
        if name is not None:
            obj.name = name
        if max_speed is not None:
            obj.max_speed = max_speed

        db.update_record("resource_type", resource_type_id, dataclasses.asdict(obj))

        return obj

    def delete(self) -> None:
        url = self.url_as_list()
        if len(url) > 1:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "specify id for deletion as in '?id=x,y'")

        # parse ids
        resource_type_ids = self.url_params.get("id")
        if not resource_type_ids:
            raise exceptions.BadRequest(detail="specify id for deletion as in '?id=x,y'")
        resource_type_ids = resource_type_ids[0].split(",")

        # validate ids
        try:
            resource_type_ids = tuple(map(int, resource_type_ids))
        except ValueError:
            raise exceptions.BadRequest(detail=f"wrong id parameters, awaiting ints")

        db.delete_records("resource_type", resource_type_ids)
        return


class ResourceController(BaseDBController):
    def create(self) -> Resource | None:
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

        return result

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

    def update(self) -> Resource:
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

        # retrieve existing Resource object
        db_data = db.retrieve_records("resource", resource_id, None)
        if not db_data:
            raise exceptions.NotFound(detail=f"object with id = {resource_id} not found")

        # update and send object data to db connection
        obj = Resource(name=db_data[0][1], resource_type_id=db_data[0][2], current_speed=db_data[0][3])
        if name is not None:
            obj.name = name
        if resource_type_id is not None:
            obj.resource_type_id = resource_type_id
        if current_speed is not None:
            obj.current_speed = current_speed

        data = dataclasses.asdict(obj)
        data.pop("speed_exceeding_percentage")
        db.update_record("resource", resource_id, data)

        return obj

    def delete(self) -> None:
        url = self.url_as_list()
        if len(url) > 1:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "specify id for deletion as in '?id=x,y'")

        # parse ids
        resource_ids = self.url_params.get("id")
        if not resource_ids:
            raise exceptions.BadRequest(detail="specify id for deletion as in '?id=x,y'")
        resource_ids = resource_ids[0].split(",")

        try:
            resource_ids = tuple(map(int, resource_ids))
        except ValueError:
            raise exceptions.BadRequest(detail=f"wrong id parameters, awaiting ints")
        db.delete_records("resource", resource_ids)
        return
