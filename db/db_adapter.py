import dataclasses
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
            # host=Config.DB_HOST,
            host='db',
            port=Config.DB_PORT,
        )

    @abstractmethod
    def create(self, obj, table_name: str):
        pass

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
    def create(self, obj, table_name: str):
        # TODO obj.validate(), but here or in controller?
        self.db.create_record(table_name, dataclasses.asdict(obj))
        return obj

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

            obj = obj_class(*attrs)
            # TODO obj_class.validate(), but it is from DB so do I need it?
            objs.append(obj)

        return objs
