def test_list_roles_success_admin(test_admin):
    response = test_admin.get("/api/v1/rbac/roles")
    assert response.status_code == 200
    roles = response.json()
    assert len(roles) >= 3
    names = [r["name"] for r in roles]
    assert "user" in names
    assert "manager" in names
    assert "admin" in names


def test_list_roles_forbidden_manager(test_manager):
    response = test_manager.get("/api/v1/rbac/roles")
    assert response.status_code == 403


def test_create_and_delete_role(test_admin):
    # 1. Create
    response = test_admin.post(
        "/api/v1/rbac/roles",
        json={"name": "guest", "description": "Read only guest"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "guest"
    role_id = data["id"]
    
    # Verify it exists
    list_resp = test_admin.get("/api/v1/rbac/roles")
    assert any(r["name"] == "guest" for r in list_resp.json())

    # 2. Delete
    delete_resp = test_admin.delete(f"/api/v1/rbac/roles/{role_id}")
    assert delete_resp.status_code == 204
    list_resp = test_admin.get("/api/v1/rbac/roles")
    assert not any(r["name"] == "guest" for r in list_resp.json())


def test_list_and_create_permissions(test_admin):
    # List
    response = test_admin.get("/api/v1/rbac/permissions")
    assert response.status_code == 200
    assert len(response.json()) >= 6

    # Create
    create_resp = test_admin.post(
        "/api/v1/rbac/permissions",
        json={"name": "test:permission"}
    )
    assert create_resp.status_code == 201
    assert create_resp.json()["name"] == "test:permission"


def test_assign_remove_permission_from_role(test_admin):
    # Setup Role & Permission
    role_resp = test_admin.post("/api/v1/rbac/roles", json={"name": "custom"})
    role_id = role_resp.json()["id"]
    
    perm_resp = test_admin.post("/api/v1/rbac/permissions", json={"name": "custom:action"})
    perm_id = perm_resp.json()["id"]

    # Assign
    assign_resp = test_admin.post(
        f"/api/v1/rbac/roles/{role_id}/permissions",
        json={"permission_id": perm_id}
    )
    assert assign_resp.status_code == 204

    # Verify Assigned
    get_perms_resp = test_admin.get(f"/api/v1/rbac/roles/{role_id}/permissions")
    assert get_perms_resp.status_code == 200
    assert len(get_perms_resp.json()) == 1
    assert get_perms_resp.json()[0]["id"] == perm_id

    # Remove
    remove_resp = test_admin.delete(f"/api/v1/rbac/roles/{role_id}/permissions/{perm_id}")
    assert remove_resp.status_code == 204

    # Verify Removed
    get_perms_resp = test_admin.get(f"/api/v1/rbac/roles/{role_id}/permissions")
    assert len(get_perms_resp.json()) == 0


def test_assign_role_to_user(test_admin, test_user):
    # test_user is logged in, but we need their ID. Let's get it via their token
    me_resp = test_user.get("/api/v1/users/me")
    user_id = me_resp.json()["id"]
    assert me_resp.json()["role"]["name"] == "user"

    # Assign Manager Role (ID 2 usually, from seed)
    assign_resp = test_admin.put(f"/api/v1/rbac/users/{user_id}/role", json={"role_id": 2})
    assert assign_resp.status_code == 200

    # Verify Upgrade
    me_resp2 = test_user.get("/api/v1/users/me")
    assert me_resp2.json()["role"]["name"] == "manager"
