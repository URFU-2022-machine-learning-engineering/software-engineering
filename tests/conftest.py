import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="session")
def t_client():
    client = TestClient(app)
    return client
