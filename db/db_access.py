from contextlib import contextmanager

import ipdb
import psycopg2

import exceptions

from . import models


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
            raise  # pass HTTPException further
        except psycopg2.Error as e:
            print("")
            print(f"e.pgcode = {e.pgcode}")
            print("")
            if e.pgcode == "23505":  # if record already exists
                raise exceptions.BadRequest(detail=f"object already exists") from e
            elif e.pgcode == "23503":  # can't find object
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
        values = tuple((data[x] for x in data))
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

    def retrieve_record(self, table_name: str, obj_id: int):
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                SELECT 
                  * 
                FROM 
                  {table_name} 
                WHERE 
                  id = (%s);
""",
                (obj_id,),
            )
            res = cur.fetchone()
            if not res:
                raise exceptions.NotFound(detail=f"object with id = {obj_id} not found")
            obj = models.ResourceType(name=res[1], max_speed=res[2])
            cur.close()
        return obj

    # def create_tables(self) -> None:
    #     sql_commands = sql_file.read()
    #     cursor = conn.cursor()
    #     cursor.execute(sql_commands)
    #     conn.commit()
    #     cursor.close()
    #
    #
    #     conn = psycopg2.connect(database="your_db", user="your_user", password="your_password", host="your_host",
    #                             port="your_port")
    #     execute_sql_script(conn, 'init_schema.sql')
    #     conn.close()
