def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200


def test_search_route(client):
    response = client.get("/search")
    assert response.status_code == 200


def test_login_route(client):
    response = client.get("/login")
    assert response.status_code == 200
