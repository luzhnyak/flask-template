def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200


def test_protected_route(client):
    response = client.get("/first")
    assert response.status_code == 200


def test_protected_route(client):
    response = client.get("/second")
    assert response.status_code == 200
