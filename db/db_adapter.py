from abc import ABC, abstractmethod
from pprint import pprint
from typing import List

from ipdb import set_trace

import exceptions
from config import Config

from .db_access import DatabaseAccess
from .models import Resource, ResourceType


class BaseDBAdapter(ABC):
    def __init__(self):
        self.db = DatabaseAccess(
            db_name=Config.DB_NAME,
            username=Config.DB_USERNAME,
            password=Config.DB_PASSWORD,
            host=Config.DB_HOST,
            # host='db',
            port=Config.DB_PORT,
        )

    # @abstractmethod
    # def create(self):
    #     pass

    @abstractmethod
    def retrieve(self, obj_class, table_name: str, obj_id: int | None, filtering_data: dict | None):
        pass

    # @abstractmethod
    # def update(self):
    #     pass
    #
    # @abstractmethod
    # def delete(self):
    #     pass


class DBAdapter(BaseDBAdapter):
    def retrieve(self, obj_class, table_name: str, obj_id: int | None, filtering_data: dict | None):
        db_data = self.db.retrieve_records(table_name, obj_id, filtering_data)
        objs = []

        if obj_id and not db_data:  # single instance not found
            raise exceptions.NotFound(detail=f"object with id = {obj_id} not found")

        attrs_num = len(obj_class.__annotations__)
        for record in db_data:
            attrs = []
            # parse attrs for any dataclass
            for i in range(1, attrs_num + 1):
                attrs.append(record[i])

            # TODO move to view!
            # res_type = self.db.retrieve_records("resource_type", resource_type_id, None)[0]
            # max_speed = res_type[2]
            # speed_exceeding = int((current_speed / max_speed - 1) * 100) if current_speed > max_speed else 0
            # resource = Resource(name=name, resource_type_id=resource_type_id, current_speed=current_speed,)
            obj = obj_class(*attrs)
            # TODO obj_class.validate()
            objs.append(obj)

        return objs
