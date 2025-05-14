import pytest


@pytest.mark.asyncio
async def test_change_password(async_client, auth_user):
    old_password = auth_user["password"]
    new_password = "newpassword123"

    response = await async_client.post(
        "/api/v1/auth/change-password",
        params={"old_password": old_password, "new_password": new_password},
        headers=auth_user["headers"],
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("message") == "Password changed successfully"

    # Проверяем, что новый пароль работает
    login_response = await async_client.post(
        "/api/v1/auth/auth-by-username",
        data={"username": auth_user["username"], "password": new_password},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
