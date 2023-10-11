from dataclasses import dataclass


@dataclass
class ResourceType:
    name: str
    max_speed: int

    # if isinstance(max_speed, str) and not max_speed.isnumeric():
    #     raise HTTPException(http.HTTPStatus.BAD_REQUEST, "max_speed has to be int")
    # if int(max_speed) <= 0:
    #     raise HTTPException(http.HTTPStatus.BAD_REQUEST, "max_speed can't be less than one")

    def __str__(self):
        return f"{self.name}"


@dataclass
class Resource:
    name: str
    resource_type_id: int
    current_speed: int
    # speed_exceeding_percentage: int | None = None

    # TODO move to dataclass model validation
    # if isinstance(resource_type_id, str) and not resource_type_id.isnumeric():
    #     raise HTTPException(http.HTTPStatus.BAD_REQUEST, "resource_type_id has to be int")
    # if isinstance(current_speed, str) and not current_speed.isnumeric():
    #     raise HTTPException(http.HTTPStatus.BAD_REQUEST, "current_speed has to be int")
    # if int(current_speed) < 0:
    #     raise HTTPException(http.HTTPStatus.BAD_REQUEST, "current_speed can't be negative")

    def __str__(self):
        return f"{self.name}"
