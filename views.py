import dataclasses
import json
from abc import ABC, abstractmethod
from typing import List

from ipdb import set_trace

import exceptions
from db.db_adapter import DBAdapter
from db.models import Resource, ResourceType


class BaseView(ABC):
    @abstractmethod
    def serialize(self):
        pass


class ResourceTypeView(BaseView):
    def __init__(self, objs: ResourceType | List[ResourceType]):
        self.objs = objs

    def serialize(self) -> str:
        json_list = [dataclasses.asdict(obj) for obj in self.objs]

        if len(json_list) == 1:  # single instance
            json_list = json_list[0]

        json_string = json.dumps(json_list)
        return json_string


class ResourceView(BaseView):
    def __init__(self, objs: List[Resource]):
        self.objs = objs

    def serialize(self) -> str:
        adapter = DBAdapter()

        json_list = []
        for obj in self.objs:
            data = dataclasses.asdict(obj)
            res_type = adapter.retrieve(ResourceType, "resource_type", obj.resource_type_id, None)[0]
            max_speed = res_type.max_speed
            data["speed_exceeding"] = (
                int((obj.current_speed / max_speed - 1) * 100) if obj.current_speed > max_speed else 0
            )

            # replace 'resource_type_id' with 'resource_type.name'
            data.pop("resource_type_id")
            data["resource_type"] = res_type.name

            json_list.append(data)

        if len(json_list) == 1:  # single instance
            json_list = json_list[0]

        json_string = json.dumps(json_list)
        return json_string
