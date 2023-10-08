from typing import List, Optional

from config import Config
from db.db_access import DatabaseAccess
from db.models import Resource

db = DatabaseAccess(
    db_name=Config.DB_NAME,
    username=Config.DB_USERNAME,
    password=Config.DB_PASSWORD,
    host=Config.DB_HOST,
    port=Config.DB_PORT,
)


class ResourceService:
    def __init__(self):
        # Initialize your service here
        pass

    def list_resources(self) -> List[Resource]:
        """
        Get a list of all resources.

        :return: List of Resource objects.
        """
        # with db_session() as session:
        with db.connect() as connection:
            resources = connection.query(Resource).all()
        return resources

    def get_resource(self, resource_id: int) -> Optional[Resource]:
        """
        Get a resource by its ID.

        :param resource_id: ID of the resource to retrieve.
        :return: Resource object if found, else None.
        """
        # with db_session() as session:
        with db.connect() as connection:
            resource = connection.query(Resource).filter(Resource.id == resource_id).first()
        return resource

    def create_resource(self, resource: Resource) -> Resource:
        """
        Create a new resource.

        :param resource: Resource object to be created.
        :return: Created Resource object.
        """
        # with db_session() as session:
        with db.connect() as connection:
            connection.add(resource)
            connection.commit()
            connection.refresh(resource)
        return resource

    def update_resource(self, resource_id: int, updated_resource_data: dict) -> Optional[Resource]:
        """
        Update a resource's data.

        :param resource_id: ID of the resource to update.
        :param updated_resource_data: Dictionary containing updated resource data.
        :return: Updated Resource object if found, else None.
        """
        # with db_session() as session:
        with db.connect() as connection:
            resource = connection.query(Resource).filter(Resource.id == resource_id).first()
            if resource:
                for key, value in updated_resource_data.items():
                    setattr(resource, key, value)
                connection.commit()
                connection.refresh(resource)
        return resource

    def delete_resource(self, resource_id: int) -> bool:
        """
        Delete a resource by its ID.

        :param resource_id: ID of the resource to delete.
        :return: True if the resource was deleted, else False.
        """
        # with db_session() as session:
        with db.connect() as connection:
            resource = connection.query(Resource).filter(Resource.id == resource_id).first()
            if resource:
                connection.delete(resource)
                connection.commit()
                return True
        return False
