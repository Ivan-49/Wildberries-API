import pytest


@pytest.mark.asyncio
async def test_get_user_info(async_client, auth_user):
    response = await async_client.get(
        "/api/v1/auth/user-info", headers=auth_user["headers"]
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == auth_user["username"]
    assert data["first_name"] == "Test"
    assert data["last_name"] == "User"
    assert data["language"] == "ru"
    assert data["is_bot"] is False
    assert data["premium_status"] is None


@pytest.mark.asyncio
async def test_logout(async_client, auth_user):
    response = await async_client.post(
        "/api/v1/auth/logout", headers=auth_user["headers"]
    )
    assert response.status_code == 200
    data = response.json()
    assert f"User {auth_user['username']} logged out successfully" in data.get(
        "message", ""
    )
