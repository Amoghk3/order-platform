def test_get_me_success(test_user):
    # test_user fixture provides a client already logged in as a normal user
    response = test_user.get("/api/v1/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"
    assert data["role"]["name"] == "user"


def test_list_users_forbidden_for_normal_user(test_user):
    response = test_user.get("/api/v1/users")
    assert response.status_code == 403


def test_list_users_forbidden_for_manager(test_manager):
    # Manager doesn't have the 'users:list' permission
    response = test_manager.get("/api/v1/users")
    assert response.status_code == 403


def test_list_users_success_for_admin(test_admin):
    # Admin has all permissions, including 'users:list'
    response = test_admin.get("/api/v1/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
