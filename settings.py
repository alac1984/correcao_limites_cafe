import os
from enum import Enum

from dotenv import load_dotenv

load_dotenv()

class Environment(Enum):
    DESE = 1
    HOMOL = 2
    PROD = 3


class Settings:
    def __init__(self, environment: Environment):
        self.environment = environment
        self.bizagi_url = self.get_bizagi_url()
        self.db = self.get_db()

    def get_bizagi_url(self):
        urls = {
            1: os.getenv('DESE_BURL'),
            2: os.getenv('HOMOL_BURL'),
            3: os.getenv('PROD_BURL')
        }

        return urls[self.environment.value]

    def get_db(self): # TODO
        urls = {
            1: os.getenv('DESE_DB'),
            2: os.getenv('HOMOL_DB'),
            3: os.getenv('PROD_DB')
        }


