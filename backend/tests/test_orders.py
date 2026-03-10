def test_create_order(test_user):
    response = test_user.post(
        "/api/v1/orders",
        json={"total_amount": "99.99"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["total_amount"] == "99.99"
    assert data["status"] == "PENDING"
    assert "id" in data


def test_list_my_orders(test_user, test_manager):
    # user creates an order
    test_user.post("/api/v1/orders", json={"total_amount": "10.00"})
    
    # user fetches their orders
    response = test_user.get("/api/v1/orders/me")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["total_amount"] == "10.00"

    # manager shouldn't naturally see the user's order in /me 
    # (they will see it in /all, but /me is only their own)
    response2 = test_manager.get("/api/v1/orders/me")
    assert response2.status_code == 200
    assert len(response2.json()) == 0


def test_list_all_orders_forbidden_user(test_user):
    response = test_user.get("/api/v1/orders/all")
    assert response.status_code == 403


def test_list_all_orders_success_manager(test_manager):
    response = test_manager.get("/api/v1/orders/all")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_all_orders_success_admin(test_admin):
    response = test_admin.get("/api/v1/orders/all")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
