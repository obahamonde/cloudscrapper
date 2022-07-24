"""

Main Class and MetaClass from BaseModel that will implement out fqlmodel ORM.

"""

from dotenv import load_dotenv
from os import getenv
load_dotenv()
FAUNA_SECRET = getenv("FAUNA_SECRET")

from faunadb.client import FaunaClient
from faunadb.errors import FaunaError
from faunadb import query as q
