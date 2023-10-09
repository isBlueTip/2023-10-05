from dataclasses import dataclass


@dataclass
class ResourceType:
    def __init__(self, name, max_speed):
        self.name = name
        self.max_speed = max_speed

    def __str__(self):
        return f"{self.name}"


@dataclass
class Resource:
    def __init__(self, name, resource_type, current_speed):
        self.name = name
        self.resource_type = resource_type
        self.current_speed = current_speed

    def __str__(self):
        return f"{self.name}"
