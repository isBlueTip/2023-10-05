import http
from http import HTTPStatus
from pprint import pprint
from typing import List

import ipdb
import psycopg2

from config import Config
from db.db_access import DatabaseAccess
from db.models import Resource, ResourceType
from exceptions import HTTPException
from services.resource_service import ResourceService
from services.resource_type_service import ResourceTypeService

db = DatabaseAccess(
    db_name=Config.DB_NAME,
    username=Config.DB_USERNAME,
    password=Config.DB_PASSWORD,
    host=Config.DB_HOST,
    port=Config.DB_PORT,
)


class ResourceTypeController:
    def __init__(
        self,
        db_service: ResourceTypeService,
        path: str,  # request path
        req_body: dict | None = None,  # data from post if exist
        url_params: dict | None = None,  # data from url - filter, anything else?
    ):
        self.db_service = db_service
        self.path = path
        self.req_body = req_body
        self.url_params = url_params
        self.create_tables()

    @staticmethod
    def create_tables():
        with db.connect() as conn:
            cur = conn.cursor()
            # check if db already populated
            cur.execute(
                '''
            SELECT 
              EXISTS (
                SELECT 
                FROM 
                  information_schema.tables 
                WHERE 
                  table_name = 'resource_type'
              );
                   '''
            )
            exists = cur.fetchone()[0]
            if not exists:
                print('not exists')
                print('')
                cur.execute(
                    '''
                CREATE TABLE resource_type (
                  id serial PRIMARY KEY, name varchar NOT NULL UNIQUE, 
                  max_speed int NOT NULL, created_at timestamp DEFAULT NOW()
                );

                CREATE TABLE resource (
                  id serial PRIMARY KEY, 
                  name varchar NOT NULL UNIQUE, 
                  type_id int REFERENCES resource_type(id), 
                  current_speed int, 
                  created_at timestamp DEFAULT NOW()
                );
                '''
                )
                # todo add fixtures
                conn.commit()
            cur.close()
            conn.close()

    def list_resource_types(self) -> List[ResourceType]:
        resource_types = self.db_service.get_all_resource_types()
        return resource_types

    def get_resource_type(self, resource_type_id: int) -> ResourceType:
        resource_type = self.db_service.get_resource_type_by_id(resource_type_id)
        if not resource_type:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource type not found")
        return resource_type

    def create(self) -> ResourceType | None:

        print(f'self.req_body = {self.req_body}')
        print('')

        # create ResourceType object and send its data to connection
        if not self.req_body:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "body contains zero data")
        name = self.req_body.get('name')
        max_speed = self.req_body.get('max_speed')
        if not all((name, max_speed)):
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "body doesn't contain some data")

        # todo validate! but where?
        obj = ResourceType(name=name, max_speed=max_speed)
        with db.connect() as conn:
            cur = conn.cursor()
            print('before executing')
            try:
                # 1/0
                cur.execute(
                    f'''
                INSERT INTO resource_type (name, max_speed) 
                VALUES 
                  (%s, %s); 
                ''',
                    (obj.name, obj.max_speed),
                )

            except psycopg2.Error as e:
                print('')
                print(f'error code = {e.pgcode}')
                print('')
                if e.pgcode == '23505':
                    raise HTTPException(status_code=http.HTTPStatus.BAD_REQUEST, detail="already exists")
            conn.commit()
        return obj

    def update_resource_type(self, resource_type_id: int, resource_type: ResourceType) -> ResourceType:
        updated_resource_type = self.db_service.update_resource_type(resource_type_id, resource_type)
        if not updated_resource_type:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource type not found")
        return updated_resource_type

    def delete_resource_type(self, resource_type_id: int) -> None:  # todo bulk delete?
        deleted = self.db_service.delete_resource_type(resource_type_id)
        if not deleted:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource type not found")


class ResourceController:
    def __init__(
        self,
        service: ResourceService,  # todo do I need to pass a ResourceService instance here?
        path: str,  # request path
        # todo naming - body?
        payload: dict = None,  # data from post if exist
        url_args: dict = None,  # data from url - filter, anything else?
    ):
        self.service = service
        self.path = path
        self.payload = payload
        self.url_args = url_args

    def list_resources(self) -> List[Resource]:
        resources = self.service.list_resources()
        return resources

    def get_resource(self, resource_id: int) -> Resource:
        resource = self.service.get_resource(resource_id)
        if not resource:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource not found")
        return resource

    def create_resource(self, resource: Resource) -> Resource:
        created_resource = self.service.create_resource(resource)
        return created_resource

    def update_resource(self, resource_id: int, resource: Resource) -> Resource:
        updated_resource = self.service.update_resource(resource_id, resource)
        if not updated_resource:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource not found")
        return updated_resource

    def delete_resource(self, resource_id: int) -> None:
        deleted = self.service.delete_resource(resource_id)
        if not deleted:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource not found")