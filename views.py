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
        # single instance
        if isinstance(self.objs, ResourceType):
            json_string = json.dumps(dataclasses.asdict(self.objs))
            return json_string
        # objects list
        elif isinstance(self.objs, list) and all(isinstance(obj, ResourceType) for obj in self.objs):
            json_list = [dataclasses.asdict(obj) for obj in self.objs]
            json_string = json.dumps(json_list)
            return json_string

        else:
            print("ERROR: while parsing json data from controller")
            raise exceptions.InternalServerError()


class ResourceView(BaseView):
    def __init__(self, objs: Resource):
        self.objs = objs

    def serialize(self) -> str:
        # set_trace()
        adapter = DBAdapter()
        if len(self.objs) == 1:  # single object
            resource = self.objs[0]

            # create dict to serialize
            data = dataclasses.asdict(resource)

            # find max_speed for this resource
            res_type = adapter.retrieve(ResourceType, "resource_type", resource.resource_type_id, None)[0]
            max_speed = res_type.max_speed
            data["speed_exceeding"] = (
                int((resource.current_speed / max_speed - 1) * 100) if resource.current_speed > max_speed else 0
            )
            json_string = json.dumps(data)
            return json_string

        elif isinstance(self.objs, list) and all(isinstance(obj, Resource) for obj in self.objs):
            json_list = []
            for obj in self.objs:
                data = dataclasses.asdict(obj)
                res_type = adapter.retrieve(ResourceType, "resource_type", obj.resource_type_id, None)[0]
                max_speed = res_type.max_speed
                data["speed_exceeding"] = (
                    int((obj.current_speed / max_speed - 1) * 100) if obj.current_speed > max_speed else 0
                )
                json_list.append(data)
            json_string = json.dumps(json_list)
            return json_string

        else:
            print("ERROR: while parsing json data from controller")
            raise exceptions.InternalServerError()
