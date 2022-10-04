import pytest
from db.queries.bg_request_q import (
    delete_bg_request,
    get_bg_types_q,
    get_specifics_works_q,
    get_user_requests_query,
)

from settings import USER_PHOTO_PATH
from sqlalchemy.ext.asyncio import AsyncSession
from db.queries.users_q import (
    get_user_by_login,
    update_user_info_q,
    delete_user_from_db,
)


class TestUserApiAuth:
    @pytest.mark.anyio
    async def test_me(
        self, async_client_auth, db_session: AsyncSession, test_register_user
    ):
        user = await get_user_by_login(db_session, test_register_user["login"])
        response = await async_client_auth.get("/user/me")

        assert response.status_code == 200

        response_data = response.json()
        assert user.login == response_data.get("login")
        assert user.email == response_data.get("email")
        assert user.phone == response_data.get("phone")

    @pytest.mark.anyio
    async def test_me_put(
        self,
        async_client_auth,
        db_session: AsyncSession,
        test_register_user,
        test_update_data_user,
    ):
        response = await async_client_auth.put("/user/me", json=test_update_data_user)

        assert response.status_code == 200

        user = await get_user_by_login(db_session, test_register_user["login"])
        assert user.inn == test_update_data_user.get("inn")
        assert user.fio == test_update_data_user.get("fio")

    @pytest.mark.anyio
    async def test_me_put_bad_inn(self, async_client_auth):
        response = await async_client_auth.put("/user/me", json={"inn": 10})
        assert response.status_code == 400

    @pytest.mark.anyio
    async def test_logout(self, async_client_auth):
        response = await async_client_auth.get("/user/logout")
        assert response.status_code == 200

    @pytest.mark.anyio
    async def test_update_photo(
        self, async_client_auth, db_session: AsyncSession, test_register_user
    ):
        file_path = USER_PHOTO_PATH.format(
            user_type="client", filename="test_image.jpg"
        )
        file = {"photo": ("user_photo.jpg", open(file_path, "rb"), "image/jpg")}
        response = await async_client_auth.post("/user/update_photo", files=file)

        assert response.status_code == 204
        user = await get_user_by_login(db_session, test_register_user["login"])
        assert user.photo.lower() == USER_PHOTO_PATH.format(
            user_type="client", filename=test_register_user["email"].lower() + ".jpg"
        )

    @pytest.mark.anyio
    async def test_update_photo_bad_data(self, async_client_auth):
        file_path = USER_PHOTO_PATH.format(user_type="client", filename="bad_test.xls")
        file = {
            "photo": ("bad_file.xls", open(file_path, "rb"), "application/vnd.ms-excel")
        }
        response = await async_client_auth.post("/user/update_photo", files=file)

        assert response.status_code == 404

    @pytest.mark.anyio
    async def test_user_delete(
        self,
        async_client_auth,
        db_session: AsyncSession,
        delete_user_data: dict,
        test_register_user,
    ):
        response = await async_client_auth.post(
            "/user/delete_user", json=delete_user_data
        )
        assert response.status_code == 200
        await update_user_info_q(db_session, test_register_user["login"], deleted=False)

    @pytest.mark.anyio
    async def test_user_delete_bad_data(
        self, async_client_auth, delete_user_bad_datas: list[dict]
    ):
        for delete_data in delete_user_bad_datas:
            response = await async_client_auth.post(
                "/user/delete_user", json=delete_data
            )
            assert response.status_code == 422

    @pytest.mark.anyio
    async def test_user_deleted_login(
        self, async_client_deleted_user, test_delete_user
    ):
        response = await async_client_deleted_user.post(
            "/user/login",
            json={
                "login": test_delete_user["login"],
                "password": test_delete_user["password"],
            },
        )
        assert response.status_code == 404


class TestUserNonAuth:
    @pytest.mark.anyio
    async def test_me(self, async_client):
        response = await async_client.get("/user/me")
        assert response.status_code == 403

    @pytest.mark.anyio
    async def test_me_put(self, async_client):
        response = await async_client.put("/user/me", json={"inn": 1231341543})
        assert response.status_code == 403

    @pytest.mark.anyio
    async def test_update_photo(self, async_client):
        file = {
            "photo": (
                "user_photo.jpg",
                open("static/images/client/test_image.jpg", "rb"),
                "image/jpg",
            )
        }
        response = await async_client.post("/user/update_photo", files=file)
        assert response.status_code == 403

    @pytest.mark.anyio
    async def test_logout(self, async_client):
        response = await async_client.get("/user/logout")
        assert response.status_code == 403

    @pytest.mark.anyio
    async def test_delete_user(self, async_client):
        response = await async_client.post(
            "/user/delete_user",
            json={"reason_deleted": "bank", "delete_text": "Test text"},
        )
        assert response.status_code == 403

    @pytest.mark.anyio
    async def test_register(self, async_client, test_user):
        response = await async_client.post("/user/signup", json=test_user)
        assert response.status_code == 201

    @pytest.mark.anyio
    async def test_register_bad_data(self, async_client, test_user):
        test_user["inn"] = 10
        response = await async_client.post("/user/signup", json=test_user)
        assert response.status_code == 400

    @pytest.mark.anyio
    async def test_regiser_existinig_user(self, async_client, test_user):
        response = await async_client.post("/user/signup", json=test_user)
        assert response.status_code == 400

    @pytest.mark.anyio
    async def test_login(self, async_client, db_session: AsyncSession, test_user):
        response = await async_client.post(
            "/user/login",
            json={"login": test_user["login"], "password": test_user["password"]},
        )
        assert response.status_code == 200
        await delete_user_from_db(db_session, test_user["login"])


class TestBGRequest:
    @pytest.mark.anyio
    async def test_create_bg_request(
        self,
        async_client_auth,
        db_session: AsyncSession,
        test_register_user,
        test_bg_request_data,
    ):
        user = await get_user_by_login(db_session, test_register_user["login"])
        user_requests = await get_user_requests_query(db_session, user.id)
        response = await async_client_auth.post(
            "/bg_request/new_bg_request", json=test_bg_request_data
        )
        current_user_requests = await get_user_requests_query(db_session, user.id)

        assert response.status_code == 200
        assert len(current_user_requests) == len(user_requests) + 1

        await delete_bg_request(db_session, current_user_requests[-1].id)

    @pytest.mark.anyio
    async def test_get_bg_request_info(
        self,
        async_client_auth,
        db_session: AsyncSession,
        test_register_user,
        test_bg_request_data,
    ):
        user = await get_user_by_login(db_session, test_register_user["login"])
        await async_client_auth.post(
            "bg_request/new_bg_request", json=test_bg_request_data
        )
        current_user_requests = await get_user_requests_query(db_session, user.id)
        response = await async_client_auth.get(
            f"/bg_request/get_user_request?request_id={current_user_requests[-1].id}"
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "Request is not ready"}
        await delete_bg_request(db_session, current_user_requests[-1].id)

    @pytest.mark.anyio
    async def test_get_bg_request_info_is_ready(
        self,
        async_client_auth,
        test_bg_request_data,
        test_register_user,
        db_session: AsyncSession,
    ):
        test_bg_request_data["is_ready"] = True
        user = await get_user_by_login(db_session, test_register_user["login"])
        await async_client_auth.post(
            "bg_request/new_bg_request", json=test_bg_request_data
        )
        current_user_requests = await get_user_requests_query(db_session, user.id)
        response = await async_client_auth.get(
            f"/bg_request/get_user_request?request_id={current_user_requests[-1].id}"
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == current_user_requests[-1].id
        assert response_data["inn"] == test_bg_request_data["inn"]
        assert (
            response_data["purchase_number"] == test_bg_request_data["purchase_number"]
        )
        await delete_bg_request(db_session, current_user_requests[-1].id)

    @pytest.mark.anyio
    async def test_get_bg_request_info_bad_data(self, async_client_auth):
        response = await async_client_auth.get(
            "/bg_request/get_user/request?request_id=1"
        )
        assert response.status_code == 404

    @pytest.mark.anyio
    async def test_get_all_bg_requests_user(
        self, async_client_auth, db_session, test_register_user
    ):
        response = await async_client_auth.get("/bg_request/get_user_requests")
        assert response.status_code == 200
        response_data = response.json()
        user = await get_user_by_login(db_session, test_register_user["login"])
        user_requests = await get_user_requests_query(db_session, user.id)
        assert len(response_data["requests"]) == len(user_requests)

    @pytest.mark.anyio
    async def test_get_bg_types(self, async_client_auth, db_session):
        response = await async_client_auth.get("/bg_request/get_bg_types")
        assert response.status_code == 200
        response_data = response.json()
        bg_types = await get_bg_types_q(db_session)
        assert len(response_data["data"]) == len(bg_types)

    @pytest.mark.anyio
    async def test_get_workspecifics_types(self, async_client_auth, db_session):
        response = await async_client_auth.get("/bg_request/get_work_specifics")
        assert response.status_code == 200
        work_specifics = await get_specifics_works_q(db_session)
        assert len(response.json()["data"]) == len(work_specifics)
