import random
from contextlib import contextmanager
from typing import Tuple

import psycopg2

import exceptions


class DatabaseAccess:
    def __init__(
        self,
        db_name: str = "postgres",
        username: str = "postgres",
        password: str = "postgres",
        host: str = "127.0.0.1",
        port: int = 5432,
    ):
        self.db_name = db_name
        self.username = username
        self.password = password
        self.host = host
        self.port = port

    @contextmanager
    def connect(self) -> None:
        connection = psycopg2.connect(
            database=self.db_name, user=self.username, password=self.password, host=self.host, port=self.port
        )
        try:
            yield connection

        except exceptions.HTTPException:
            raise  # catch HTTPException further

        except psycopg2.Error as e:
            if e.pgcode == "23505":  # if record already exists
                raise exceptions.BadRequest(detail=f"object already exists") from e
            elif e.pgcode == "23503":  # can't find record
                raise exceptions.BadRequest(detail=f"can't find an object with given id") from e
            else:
                print(f"ERROR: can't connect to database: {e}, code: {e.pgcode}")
                raise exceptions.InternalServerError(detail=str(e)) from e

        except Exception as e:
            print(f"ERROR: can't connect to database: {e}")

        finally:
            connection.close()

    def create_record(self, table_name: str, data: dict):
        columns = ", ".join(x for x in data)
        values = tuple(data.values())
        placeholders = ", ".join("%s" for x in data)

        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                INSERT INTO
                  {table_name} ({columns})
                VALUES
                  ({placeholders});
""",
                values,
            )
            conn.commit()
            cur.close()

    def update_record(self, table_name: str, obj_id: int, data: dict):
        values = tuple(data.values())
        values += (obj_id,)
        set_placeholders = [f"{column} = %s" for column in data]
        set_placeholders = ", ".join(set_placeholders)

        with self.connect() as conn:
            cur = conn.cursor()
            query = f"""
            UPDATE 
              {table_name} 
            SET 
              {set_placeholders}
            WHERE 
              id = %s;
"""
            cur.execute(query, values)
            conn.commit()
            cur.close()

    def retrieve_records(self, table_name: str, obj_id: int | None, filtering_dict: dict | None):
        query = f"""
                SELECT 
                  * 
                FROM 
                  {table_name} 
"""

        # either resource_id or filtering
        if obj_id:
            query += """
            WHERE
              id = (%s)
            """
        elif filtering_dict:
            filtering_args = filtering_dict["type_id"]
            if len(filtering_args) == 1:  # add bracket for single object
                filtering_args = f"({filtering_args[0]})"
            query += f"""
            WHERE
              resource_type_id IN {filtering_args}
            """

        query += ";"

        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute(query, (obj_id,))

            res = cur.fetchall()
            cur.close()
        return res

    def delete_records(self, table_name: str, obj_ids: int | Tuple[int]):
        if len(obj_ids) == 1:  # add bracket for single object
            obj_ids = f"({obj_ids[0]})"
        query = f"""
                DELETE
                FROM 
                  {table_name}
                WHERE
                  id IN {obj_ids};
"""
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute(
                query,
                (obj_ids,),
            )

            conn.commit()
            cur.close()
        return

    def create_tables(self) -> None:
        with self.connect() as conn:
            cur = conn.cursor()
            query = """
            CREATE TABLE resource_type (
              id serial PRIMARY KEY, name varchar NOT NULL UNIQUE, 
              max_speed int NOT NULL, created_at timestamp DEFAULT NOW()
            );
            CREATE TABLE resource (
              id serial PRIMARY KEY, 
              name varchar NOT NULL UNIQUE, 
              resource_type_id int REFERENCES resource_type(id) ON DELETE CASCADE, 
              current_speed int, 
              created_at timestamp DEFAULT NOW()
            );
             """
            cur.execute(query)

            conn.commit()
            cur.close()

    def insert_fixtures(self) -> None:
        types = [
            {"name": "loader", "max_speed": 50},
            {"name": "excavator", "max_speed": 40},
            {"name": "rig", "max_speed": 70},
            {"name": "truck", "max_speed": 80},
            {"name": "grader", "max_speed": 40},
        ]
        with self.connect() as conn:
            cur = conn.cursor()

            # create five resource_types
            for data in types:
                columns = ", ".join(x for x in data)
                values = tuple(data.values())
                placeholders = ", ".join("%s" for x in data)
                query = f""" INSERT INTO
                      resource_type ({columns})
                    VALUES
                      ({placeholders});
                """
                cur.execute(query, values)

            # create 5 x 5 resources
            for i in range(1, 6):
                types = {
                    1: "L",
                    2: "E",
                    3: "R",
                    4: "T",
                    5: "G",
                }
                for _ in range(0, 5):
                    name = types[i] + str(random.randint(0, 100))
                    data = {"name": name, "resource_type_id": i, "current_speed": random.randint(0, 100)}
                    columns = ", ".join(x for x in data)
                    values = tuple(data.values())
                    placeholders = ", ".join("%s" for x in data)
                    query = f""" INSERT INTO
                          resource ({columns})
                        VALUES
                          ({placeholders});
                    """
                    cur.execute(query, values)
            conn.commit()
            cur.close()
