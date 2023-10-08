import os

import dotenv

dotenv.load_dotenv()


class Config:
    DB_NAME = os.getenv('DB_NAME', default='reksoft')
    DB_USERNAME = os.getenv('DB_USERNAME', default='postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', default='postgres')
    DB_HOST = os.getenv('DB_HOST', default='localhost')
    DB_PORT = os.getenv('DB_PORT', default=5432)
