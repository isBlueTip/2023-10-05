from dataclasses import dataclass


@dataclass
class ResourceType:
    name: str
    max_speed: int

    def __str__(self):
        return f"{self.name}"


@dataclass
class Resource:
    name: str
    resource_type: int
    current_speed: int

    def __str__(self):
        return f"{self.name}"
