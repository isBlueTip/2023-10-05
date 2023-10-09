from typing import List, Optional

from config import Config
from db.db_access import DatabaseAccess
from db.models import ResourceType

db = DatabaseAccess(
    db_name=Config.DB_NAME,
    username=Config.DB_USERNAME,
    password=Config.DB_PASSWORD,
    host=Config.DB_HOST,
    port=Config.DB_PORT,
)


class ResourceTypeService:
    def __init__(self):
        # Initialize your service here
        pass

    def list_resource_types(self) -> List[ResourceType]:
        """
        Get a list of all resource types.

        :return: List of ResourceType objects.
        """
        # with db_session() as session:
        with db.connect() as connection:
            resource_types = connection.query(ResourceType).all()
        return resource_types

    def get_resource_type_by_id(resource_type_id: int) -> Optional[ResourceType]:
        """
        Get a resource type by its ID.

        :param resource_type_id: ID of the resource type to retrieve.
        :return: ResourceType object if found, else None.
        """
        # with db_session() as session:
        with db.connect() as connection:
            resource_type = connection.query(ResourceType).filter(ResourceType.id == resource_type_id).first()
        return resource_type

    def create_resource_type(resource_type: ResourceType) -> ResourceType:
        """
        Create a new resource type.

        :param resource_type: ResourceType object to be created.
        :return: Created ResourceType object.
        """
        # with db_session() as session:
        with db.connect() as connection:
            connection.add(resource_type)
            connection.commit()
            connection.refresh(resource_type)
        return resource_type

    def update_resource_type(resource_type_id: int, updated_resource_type_data: dict) -> Optional[ResourceType]:
        """
        Update a resource type's data.

        :param resource_type_id: ID of the resource type to update.
        :param updated_resource_type_data: Dictionary containing updated resource type data.
        :return: Updated ResourceType object if found, else None.
        """
        # with db_session() as session:
        with db.connect() as connection:
            resource_type = connection.query(ResourceType).filter(ResourceType.id == resource_type_id).first()
            if resource_type:
                for key, value in updated_resource_type_data.items():
                    setattr(resource_type, key, value)
                connection.commit()
                connection.refresh(resource_type)
        return resource_type

    def delete_resource_type(resource_type_id: int) -> bool:
        """
        Delete a resource type by its ID.

        :param resource_type_id: ID of the resource type to delete.
        :return: True if the resource type was deleted, else False.
        """
        # with db_session() as session:
        with db.connect() as connection:
            resource_type = connection.query(ResourceType).filter(ResourceType.id == resource_type_id).first()
            if resource_type:
                connection.delete(resource_type)
                connection.commit()
                return True
        return False
