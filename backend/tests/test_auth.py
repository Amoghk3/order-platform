def test_register_user_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    # The default role is assigned by the DB
    assert data["role"]["name"] == "user"


def test_register_duplicate_email(client):
    # First save
    client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "password123"}
    )
    # Second try
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "password123"}
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_login_success(client):
    # Register first
    client.post(
        "/api/v1/auth/register",
        json={"email": "loginn@example.com", "password": "password123"}
    )
    # Attempt login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "loginn@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "login_wrong@example.com", "password": "password123"}
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "login_wrong@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert "Invalid credentials" in response.json()["detail"]


def test_login_invalid_user(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "does_not_exist@example.com", "password": "password"}
    )
    assert response.status_code == 400
    assert "Invalid credentials" in response.json()["detail"]
