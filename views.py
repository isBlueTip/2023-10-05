import dataclasses
import json

from db.models import Resource, ResourceType


class BaseSerializer:
    pass


class ResourceTypeSerializer(BaseSerializer):
    def __init__(self, obj: ResourceType):
        self.obj = obj

    def serialize(self) -> str:
        # json_string = json.dumps(self.obj)
        json_string = json.dumps(dataclasses.asdict(self.obj))
        return json_string


class ResourceSerializer(BaseSerializer):
    pass
