from fastapi.testclient import TestClient
from src.univention.scim.server.main import app


client = TestClient(app)


def test_read_main() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
