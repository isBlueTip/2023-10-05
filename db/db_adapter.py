import dataclasses
from abc import ABC, abstractmethod
from typing import Tuple

import exceptions
from config import Config

from .db_access import DatabaseAccess


class BaseDBAdapter(ABC):
    def __init__(self):
        self.db = DatabaseAccess(
            db_name=Config.DB_NAME,
            username=Config.DB_USERNAME,
            password=Config.DB_PASSWORD,
            # host=Config.DB_HOST,
            host="db",
            port=Config.DB_PORT,
        )

        # check if db tables exist; init and populate if not
        self.init_tables()

    def init_tables(self) -> None:
        with self.db.connect() as conn:
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

        if not exists:  # create and populate tables if not exist
            self.db._create_tables()
            self.db._insert_fixtures()

    @abstractmethod
    def create(self, obj, table_name: str):
        pass

    @abstractmethod
    def retrieve(self, obj_class, table_name: str, obj_id: int | None, filtering_data: dict | None):
        pass

    @abstractmethod
    def update(self, obj, table_name: str, obj_id: int | None):
        pass

    @abstractmethod
    def delete(self, table_name: str, obj_ids: Tuple[int]):
        pass


class DBAdapter(BaseDBAdapter):
    def create(self, obj, table_name: str):
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
            objs.append(obj)

        return objs

    def update(self, obj, table_name: str, obj_id: int):
        self.db.update_record(table_name, obj_id, dataclasses.asdict(obj))

        return obj

    def delete(self, table_name: str, obj_ids: Tuple[int]):
        self.db.delete_records(table_name, obj_ids)
