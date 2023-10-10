import dataclasses
import json
from abc import ABC, abstractmethod

from db.models import Resource, ResourceType


class BaseSerializer(ABC):
    @abstractmethod
    def serialize(self):
        pass


class ResourceTypeSerializer(BaseSerializer):
    def __init__(self, obj: ResourceType):
        self.obj = obj

    def serialize(self) -> str:
        json_string = json.dumps(dataclasses.asdict(self.obj))
        return json_string


class ResourceSerializer(BaseSerializer):
    def __init__(self, obj: Resource):
        self.obj = obj

    def serialize(self) -> str:
        json_string = json.dumps(dataclasses.asdict(self.obj))
        return json_string
