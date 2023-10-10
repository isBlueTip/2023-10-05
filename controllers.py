import dataclasses
import http
from abc import ABC, abstractmethod

import exceptions
from config import Config
from db.db_access import DatabaseAccess
from db.models import Resource, ResourceType
from exceptions import HTTPException

db = DatabaseAccess(
    db_name=Config.DB_NAME,
    username=Config.DB_USERNAME,
    password=Config.DB_PASSWORD,
    host=Config.DB_HOST,
    port=Config.DB_PORT,
)


class BaseDBController(ABC):
    def __init__(
        self,
        path: str,  # request path
        req_body: dict | None = None,  # data from post if exist
        url_params: dict | None = None,  # data from url - filter, anything else?
    ):
        self.path = path
        self.req_body = req_body
        self.url_params = url_params
        self.init_tables()

    @staticmethod
    def init_tables() -> None:
        with db.connect() as conn:
            cur = conn.cursor()
            cur.execute(  # check if tables in db already exist
                """
            SELECT 
              EXISTS (
                SELECT 
                FROM 
                  information_schema.tables 
                WHERE 
                  table_name = 'resource_type'
              );
                   """
            )
            exists = cur.fetchone()[0]
            cur.close()
        if not exists:  # create tables if not exist
            db.create_tables()
            db.insert_fixtures()

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def delete(self):
        pass


class ResourceTypeController(BaseDBController):
    def get(self) -> ResourceType:
        # parse id
        if len(self.path.split("/")) > 2:
            resource_type_id = self.path.split("/")[-1]
            if not resource_type_id.isnumeric():  # not numeric argument
                raise exceptions.NotFound(detail=f"{resource_type_id} not found")
            resource_type_id = int(resource_type_id)
        else:
            resource_type_id = None
        db_data = db.retrieve_records("resource_type", resource_type_id)
        objs = []
        if resource_type_id:  # single instance
            if not db_data:
                raise exceptions.NotFound(detail=f"object with id = {resource_type_id} not found")
            objs = ResourceType(name=db_data[0][1], max_speed=db_data[0][2])
        else:  # multiple instances
            for obj in db_data:
                print(f"obj = {obj}")
                objs.append(ResourceType(name=obj[1], max_speed=obj[2]))
        return objs

    def create(self) -> ResourceType | None:
        # validate request data
        if not self.req_body:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "request body contains no data")
        name = self.req_body.get("name")
        max_speed = self.req_body.get("max_speed")

        if not name:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "you have to specify name")
        if not max_speed:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "you have to specify max_speed")
        if int(max_speed) <= 0:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "max_speed can't be less than one")

        # create ResourceType object and send its data to db connection
        obj = ResourceType(name=name, max_speed=max_speed)

        db.create_record("resource_type", dataclasses.asdict(obj))

        return obj

    def update(self) -> ResourceType:
        # validate request data
        resource_type_id = self.path.split("/")[-1]
        if not resource_type_id.isnumeric():  # not numeric argument
            raise exceptions.NotFound(detail=f"{resource_type_id} not found")
        resource_type_id = int(resource_type_id)

        if not self.req_body:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "request body contains no data")
        name = self.req_body.get("name")
        max_speed = self.req_body.get("max_speed")
        if not any((name, max_speed)):
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "at least one attribute to change have to be specified")

        # retrieve existing ResourceType object, update and send its data to db connection
        db_data = db.retrieve_records("resource_type", resource_type_id)
        if not db_data:
            raise exceptions.NotFound(detail=f"object with id = {resource_type_id} not found")
        obj = ResourceType(name=db_data[0][1], max_speed=db_data[0][2])
        if name:
            obj.name = name
        if max_speed:
            obj.max_speed = max_speed

        db.update_record("resource_type", resource_type_id, dataclasses.asdict(obj))

        return obj

    def delete(self) -> None:
        # parse ids
        resource_type_ids = self.url_params.get("id")
        if not resource_type_ids:
            raise exceptions.BadRequest(detail=f"wrong id parameters")

        resource_type_ids = resource_type_ids[0].split(",")
        try:
            resource_type_ids = tuple(map(int, resource_type_ids))
        except ValueError:
            raise exceptions.BadRequest(detail=f"wrong id parameters")
        db.delete_records("resource_type", resource_type_ids)
        return


class ResourceController(BaseDBController):
    def get(self) -> Resource:
        # parse id
        if len(self.path.split("/")) > 2:
            resource_id = self.path.split("/")[-1]
            if not resource_id.isnumeric():  # not numeric argument
                raise exceptions.NotFound(detail=f"{resource_id} not found")
            resource_id = int(resource_id)
        else:
            resource_id = None

        # parse filtering params
        type_ids = self.url_params.get("type")

        if type_ids:
            type_ids = type_ids[0].split(",")
            try:
                type_ids = tuple(map(int, type_ids))
            except ValueError:
                raise exceptions.BadRequest(detail=f"wrong type url parameters")
            filtering_data = {"type_id": type_ids}
        else:
            filtering_data = {}
        db_data = db.retrieve_records("resource", resource_id, filtering_data)
        objs = []
        if resource_id:  # single instance
            if not db_data:
                raise exceptions.NotFound(detail=f"object with id = {resource_id} not found")
            name = db_data[0][1]
            resource_type_id = db_data[0][2]
            current_speed = db_data[0][3]
            res_type = db.retrieve_records("resource_type", resource_type_id, None)[0]
            max_speed = res_type[2]
            speed_exceeding = int((current_speed / max_speed - 1) * 100) if current_speed > max_speed else 0
            objs = Resource(
                name=name,
                resource_type_id=resource_type_id,
                current_speed=current_speed,
                speed_exceeding_percentage=speed_exceeding,
            )
        else:  # multiple instances
            for obj in db_data:
                name = obj[1]
                resource_type_id = obj[2]
                current_speed = obj[3]
                res_type = db.retrieve_records("resource_type", resource_type_id, None)[0]
                max_speed = res_type[2]
                speed_exceeding = int((current_speed / max_speed - 1) * 100) if current_speed > max_speed else 0
                objs.append(
                    Resource(
                        name=name,
                        resource_type_id=resource_type_id,
                        current_speed=current_speed,
                        speed_exceeding_percentage=speed_exceeding,
                    )
                )
        return objs

    def create(self) -> Resource | None:
        # validate request data
        if not self.req_body:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "request body contains no data")
        name = self.req_body.get("name")
        resource_type = self.req_body.get("resource_type")
        current_speed = self.req_body.get("current_speed")

        if not name:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "you have to specify name")
        if not resource_type:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "you have to specify resource_type")
        if not current_speed:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "you have to specify current_speed")
        if int(current_speed) < 0:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "current_speed can't be negative")

        # create Resource object and send its data to db connection
        obj = Resource(name=name, resource_type_id=resource_type, current_speed=current_speed)

        db.create_record("resource", dataclasses.asdict(obj))

        return obj

    def update(self) -> Resource:
        # validate request data
        resource_id = self.path.split("/")[-1]
        if not resource_id.isnumeric():  # not numeric argument
            raise exceptions.NotFound(detail=f"{resource_id} not found")
        resource_id = int(resource_id)

        if not self.req_body:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "request body contains no data")
        name = self.req_body.get("name")
        resource_type_id = self.req_body.get("resource_type_id")
        current_speed = self.req_body.get("current_speed")
        if not any((name, resource_type_id, current_speed)):
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "at least one attribute to change have to be specified")

        # retrieve existing ResourceType object, update and send its data to db connection
        db_data = db.retrieve_records("resource", resource_id)
        if not db_data:
            raise exceptions.NotFound(detail=f"object with id = {resource_id} not found")

        obj = Resource(name=db_data[0][1], resource_type_id=db_data[0][2], current_speed=db_data[0][3])
        if name:
            obj.name = name
        if resource_type_id:
            obj.resource_type_id = resource_type_id
        if current_speed:
            obj.current_speed = current_speed

        db.update_record("resource", resource_id, dataclasses.asdict(obj))

        return obj

    def delete(self) -> None:
        # parse ids
        resource_ids = self.url_params.get("id")
        if not resource_ids:
            raise exceptions.BadRequest(detail=f"wrong id parameters")

        resource_ids = resource_ids[0].split(",")
        try:
            resource_ids = tuple(map(int, resource_ids))
        except ValueError:
            raise exceptions.BadRequest(detail=f"wrong id parameters")
        db.delete_records("resource", resource_ids)
        return
