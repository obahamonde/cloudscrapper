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
from faunadb.client import FaunaClient
from faunadb.errors import FaunaError
from typing import Callable, List
from pydantic import BaseModel, BaseConfig
from typing import Dict
from json import loads, dumps

fql: Callable = FaunaClient(FAUNA_SECRET).query

def createCollection(model: BaseModel):
    try:
        fql(
        q.if_(
            q.exists(q.collection(f"{model.__class__.__name__.lower()}s")),
            True,
            q.create_collection(
                {"name": f"{model.__class__.__name__.lower()}s"})))
        fql(q.create_index(
            {"name": f"{model.__class__.__name__}s".lower(), "source": q.collection(f"{model.__class__.__name__.lower()}s")}))  
    except FaunaError as e:
        print(e)
        return False
    return True
    
def createFieldIndex(model: BaseModel, field: str):
    index = {
        "name": f"{model.__class__.__name__}_by_{field}".lower(),
        "source": q.collection(f"{model.__class__.__name__}s".lower()),
        "terms": [{
            "field": ["data", field]
        }]
    }
    response = fql(
        q.if_(q.exists(q.index(q.select("name", index))), True,
              q.create_index(index)))
    return response

def createSortIndex(model: BaseModel, field: str):
    index = {
        "name": f"{model.__class__.__name__}_sort_by_{field}".lower(),
        "source": q.collection(f"{model.__class__.__name__}s".lower()),
        "terms": [{
            "field": ["data", field]
        }],
        "values": [
            {
                "field": ["ref"]
            },
        ]
    }
    response = fql(
        q.if_(q.exists(q.index(q.select("name", index))), True,
              q.create_index(index)))
    return response

class FQLModelMetaClass(BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self):
        createCollection(self)
        for field in self.__fields__:
            createFieldIndex(self, field)
            createSortIndex(self, field)
        try:
            response = fql(
                    q.create(q.collection(f"{self.__class__.__name__.lower()}s"),
                            {"data": self.dict()}))
            print(response)
            return response['data']
        except FaunaError as e:
            print(e)
            return False


    def create(self):
        createCollection(self)
        for field in self.__fields__:
            createFieldIndex(self, field)
            createSortIndex(self, field)
        for field in self.__fields__:    
            try:
                response = fql(
                    q.get(
                        q.match(
                            q.index(
                                f"{self.__class__.__name__}_by_{field}".lower()),
                            self.dict()[field])))
                print(response)
                return response['data']
            except FaunaError as e:
                response = fql(
                    q.create(q.collection(f"{self.__class__.__name__.lower()}s"),
                            {"data": self.dict()}))
                print(response)
                return response['data']

    @classmethod
    def read(self, field: str, value: str) -> BaseModel:
        try:
            response = fql(
                q.get(q.match(q.index(f"{self.__name__}_by_{field}".lower()), value)))
            return response
        except FaunaError as e:
            print(e)
            return None

    @classmethod
    def update(self, field: str, value: str, data: dict) -> BaseModel:
        try:
            response = fql(
                q.get(q.match(q.index(f"{self.__name__}_by_{field}".lower()), value)))
            fql(q.update(response['ref'], {"data": data}))
            return self.read(field, value)
        except FaunaError as e:
            print(e)
            return None

    @classmethod
    def delete(self, field: str, value: str) -> BaseModel:
        try:  
            response = fql(
                    q.get(q.match(q.index(f"{self.__name__}_by_{field}".lower()), value)))
            fql(q.delete(response['ref']))
            return response
        except FaunaError as e:
            print(e)
            return None

    @classmethod
    def read_all(self, limit: int) -> List[BaseModel]:
        try:
            index = {
                "name": f"{self.__name__}s".lower(),
                "source": q.collection(f"{self.__name__}s".lower())
            }
            fql(
                q.if_(q.exists(q.index(q.select("name", index))), True,
                      q.create_index(index)))
            refs = fql(q.paginate(q.match(f"{self.__name__}s".lower()), limit))['data']
            return [fql(q.get(ref)) for ref in refs]
        except FaunaError as e:
            print(e)
            return []
            

    @classmethod
    def find_many(self, field: str, value: str, limit: int) -> List[BaseModel]:
        try:
            index = {
                "name": f"{self.__name__}_by_{field}".lower(),
                "source": q.collection(f"{self.__name__}s".lower()),
                "terms": [{
                    "field": ["data", field]
                }]
            }
            fql(
                q.if_(q.exists(q.index(q.select("name", index))), True,
                      q.create_index(index)))
            refs = fql(q.paginate(q.match(f"{self.__name__}_by_{field}".lower(), value), limit))['data']
            return [fql(q.get(ref))['data'] for ref in refs]
        except FaunaError as e:
            print(e)
            return []

    @classmethod
    def __schema__(self)->Dict:
        return dict(loads(dumps(str(self.__dict__['__fields__']).replace("'","")).replace('(', ":{").replace(")","}").replace('=',":").replace(',', "','").replace("'{","{").replace(":","':'").replace("{","{'").replace("' ModelField':'","").replace('"',"").replace("'", '"').replace('}"', '"}').replace(' ', '').replace('}}', '"}}').replace('"True"','true').replace('"False"','false')))

    @classmethod
    def __json__(self)->str:
        return dumps(self.schema())


class FQLModel(FQLModelMetaClass):
    class Config(BaseConfig):
        orm_mode = True
        arbitrary_types_allowed = True
    

    