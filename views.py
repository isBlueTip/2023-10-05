import dataclasses
import json
from abc import ABC, abstractmethod
from typing import List

import exceptions
from db.models import Resource, ResourceType


class BaseSerializer(ABC):
    @abstractmethod
    def serialize(self):
        pass


class ResourceTypeSerializer(BaseSerializer):
    def __init__(self, objs: ResourceType | List[ResourceType]):
        self.objs = objs

    def serialize(self) -> str:
        if isinstance(self.objs, ResourceType):
            json_string = json.dumps(dataclasses.asdict(self.objs))
            return json_string
        elif isinstance(self.objs, list) and all(isinstance(obj, ResourceType) for obj in self.objs):
            json_list = [dataclasses.asdict(obj) for obj in self.objs]
            json_string = json.dumps(json_list)
            return json_string
        print("ERROR: while jsoning data from controller")
        raise exceptions.InternalServerError()


class ResourceSerializer(BaseSerializer):
    def __init__(self, objs: Resource):
        self.objs = objs

    def serialize(self) -> str:
        if isinstance(self.objs, Resource):
            json_string = json.dumps(dataclasses.asdict(self.objs))
            return json_string
        elif isinstance(self.objs, list) and all(isinstance(obj, Resource) for obj in self.objs):
            json_list = [dataclasses.asdict(obj) for obj in self.objs]
            json_string = json.dumps(json_list)
            return json_string
        print("ERROR: while jsoning data from controller")
        raise exceptions.InternalServerError()
