import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def t_client():
    from main import app

    client = TestClient(app)
    return client
