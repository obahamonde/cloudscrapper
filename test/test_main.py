"""

Test Suites based on Pytest Framework

"""

from fqlmodel.orm import FQLModelMetaClass as QM, FQLModel as Q
from names import get_full_name

from fqlmodel.utils import id as get_id, now as get_now , avatar as get_avatar, get_full_name
import pytest


class Mock(Q):
    uid:str
    name:str
    picture:str
    created_at:str


mock = Mock(uid=get_id(),name=get_full_name(),picture=get_avatar(),created_at=get_now()).create()





def test_type():
    assert type(Q) == type(QM)


def test_schema():
    assert type(Mock.__schema__()) == dict

def test_json():
    assert type(Mock.__json__()) == str

def test_create():
    id = get_id()
    now = get_now()
    avatar = get_avatar()
    full_name = get_full_name()
    mock = Mock(id=id,name=full_name,picture=avatar,created_at=now).create()
    assert mock['id'] == id

def test_save():
    id = get_id()
    now = get_now()
    avatar = get_avatar()
    full_name = get_full_name()
    mock = Mock(id=id,name=full_name,picture=avatar,created_at=now).save()
    assert mock['id'] == id

def test_find():
    id = get_id()
    now = get_now()
    avatar = get_avatar()
    full_name = get_full_name()
    Mock(id=id,name=full_name,picture=avatar,created_at=now).create()
    mock = Mock.read("id",id)
    assert mock['data']['id'] == id

def test_update():
    id = get_id()
    now = get_now()
    avatar = get_avatar()
    full_name = get_full_name()
    Mock(id=id,name=full_name,picture=avatar,created_at=now).create()
    mock = Mock.update("id",id,{
        "name":"test"
    })
    assert mock['data']['name'] == "test"

def test_delete():
    id = get_id()
    now = get_now()
    avatar = get_avatar()
    full_name = get_full_name()
    Mock(id=id,name=full_name,picture=avatar,created_at=now).create()
    mock = Mock.delete("id",id)
    assert mock['data']['id'] == id

