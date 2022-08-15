import pytest

from settings import USER_PHOTO_PATH
from sqlalchemy.ext.asyncio import AsyncSession
from db.queries.users_q import get_user_by_login, update_user_info_q, delete_user_from_db
from conftest import test_user, test_update_data


class TestUserApiAuth:
    
    @pytest.mark.anyio
    async def test_me(self, async_client_auth, db_session: AsyncSession):
        user = await get_user_by_login(db_session, test_user['login'])
        response = await async_client_auth.get('/user/me')

        assert response.status_code == 200

        response_data = response.json()
        assert user.login == response_data.get('login')
        assert user.email == response_data.get('email')
        assert user.phone == response_data.get('phone')
    
    @pytest.mark.anyio
    async def test_me_put(self, async_client_auth, db_session: AsyncSession):
        response = await async_client_auth.put('/user/me', json=test_update_data)

        assert response.status_code == 200

        user = await get_user_by_login(db_session, test_user['login'])
        assert user.inn == test_update_data.get('inn')
        assert user.fio == test_update_data.get('fio')

    @pytest.mark.anyio
    async def test_me_put_bad_inn(self, async_client_auth):
        response = await async_client_auth.put('/user/me', json={'inn': 10})
        assert response.status_code == 400


    @pytest.mark.anyio
    async def test_logout(self, async_client_auth):
        response = await async_client_auth.get('/user/logout')
        assert response.status_code == 200


    @pytest.mark.anyio
    async def test_update_photo(self, async_client_auth, db_session: AsyncSession):
        file_path = USER_PHOTO_PATH.format(user_type='client', filename='test_image.jpg')
        file = {'photo': ('user_photo.jpg', open(file_path, 'rb'), 'image/jpg')}
        response = await async_client_auth.post('/user/update_photo', files=file)

        assert response.status_code == 204
        user = await get_user_by_login(db_session, test_user['login'])
        assert user.photo.lower() == USER_PHOTO_PATH.format(user_type='client',
                filename=test_user['email'].lower() + '.jpg')

    @pytest.mark.anyio
    async def test_update_photo_bad_data(self, async_client_auth):
        file_path = USER_PHOTO_PATH.format(user_type='client', filename='bad_test.xls')
        file = {'photo': ('bad_file.xls', open(file_path, 'rb'), 'application/vnd.ms-excel')}
        response = await async_client_auth.post('/user/update_photo', files=file)

        assert response.status_code == 404
    
    @pytest.mark.anyio
    async def test_user_delete(self, async_client_auth, db_session: AsyncSession, delete_user_datas: list[dict]):
        for delete_data in delete_user_datas:
            response = await async_client_auth.post('/user/delete_user',
                        json=delete_data)
            assert response.status_code == 200
        await update_user_info_q(db_session, test_user['login'], deleted=False)

    @pytest.mark.anyio
    async def test_user_delete_bad_data(self, async_client_auth, delete_user_bad_datas: list[dict]):
        for delete_data in delete_user_bad_datas:
            response = await async_client_auth.post('/user/delete_user',
                    json=delete_data)
            assert response.status_code == 422
        


class TestUserNonAuth:

    @pytest.mark.anyio
    async def test_me(self, async_client):
        response = await async_client.get('/user/me')
        assert response.status_code == 403

    @pytest.mark.anyio
    async def test_me_put(self, async_client):
        response = await async_client.put('/user/me', json={
                'inn': 1231341543
            })
        assert response.status_code == 403

    @pytest.mark.anyio
    async def test_update_photo(self, async_client):
        file = {'photo': ('user_photo.jpg', open('static/images/client/test_image.jpg', 'rb'), 'image/jpg')}
        response = await async_client.post('/user/update_photo', files=file)
        assert response.status_code == 403

    @pytest.mark.anyio
    async def test_logout(self, async_client):
        response = await async_client.get('/user/logout')
        assert response.status_code == 403

    @pytest.mark.anyio
    async def test_delete_user(self, async_client):
        response = await async_client.post('/user/delete_user', json={
                'reason_deleted': 'bank',
                'delete_text': 'Test text'
            })
        assert response.status_code == 403

    @pytest.mark.anyio
    async def test_register(self, async_client, test_register_user):
        response = await async_client.post('/user/signup', json=test_register_user)
        assert response.status_code == 201

    @pytest.mark.anyio
    async def test_register_bad_data(self, async_client, test_register_user):
        test_user['inn'] = 10
        response = await async_client.post('/user/signup', json=test_register_user)
        assert response.status_code == 400


    @pytest.mark.anyio
    async def test_regiser_existinig_user(self, async_client, test_register_user):
        response = await async_client.post('/user/signup', json=test_register_user)
        assert response.status_code == 400


    @pytest.mark.anyio
    async def test_login(self, async_client, db_session: AsyncSession, test_register_user):
        response = await async_client.post('/user/login', json={
                'login': test_register_user['login'],
                'password': test_register_user['password']
            })
        assert response.status_code == 200
        await delete_user_from_db(db_session, test_register_user['login'])
