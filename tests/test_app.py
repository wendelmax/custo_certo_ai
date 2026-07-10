import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as c:
        yield c


def test_index_route(client):
    res = client.get('/')
    assert res.status_code == 200


def test_analisar_sem_arquivos(client):
    res = client.post('/analisar')
    assert res.status_code == 400
