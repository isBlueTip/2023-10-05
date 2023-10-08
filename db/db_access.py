from contextlib import contextmanager

import psycopg2


class DatabaseAccess:
    def __init__(
        self,
        db_name: str = 'postgres',
        username: str = 'postgres',
        password: str = 'postgres',
        host: str = '127.0.0.1',
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
        except Exception as e:
            print(f"ERROR: cant connect to database: {e}")
        finally:
            connection.close()


# Add database access methods here
