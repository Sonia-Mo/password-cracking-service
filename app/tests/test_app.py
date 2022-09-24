import pytest
from httpx import AsyncClient
from app.main import app
import ray
from app.routers.input_processing import check_interval


async def invoke_service_with(file_content):
    with open('file.txt', 'wb') as f:
        f.write(file_content)
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        with open('file.txt', 'rb+') as f:
            response = await client.post("/upload-file/", files={"client_input": f})
    return response


@pytest.mark.anyio
async def test_one_hash():
    response = await invoke_service_with(b'62f8b0e0f9d05354175a81e6e05dce87')
    assert response.status_code == 200
    assert response.json() == {"62f8b0e0f9d05354175a81e6e05dce87": "0523060685"}


@pytest.mark.anyio
async def test_empty_file():
    response = await invoke_service_with(b'')
    assert response.status_code == 406
    assert response.json() == {"detail": "Input is not valid - file is empty!"}


@pytest.mark.anyio
async def test_non_phone_number():
    # MD5 hash corresponds to 123 password
    response = await invoke_service_with(b'202cb962ac59075b964b07152d234b70')
    assert response.status_code == 406
    assert response.json() == {"detail": "Input is not valid - only phone number password is allowed"}


@pytest.mark.anyio
async def test_non_MD5_hash():
    response = await invoke_service_with(b'202cb962ac590')
    assert response.status_code == 406
    assert response.json() == {"detail": "Input is not valid - only MD5 hashes are acceptable"}


@pytest.mark.anyio
async def test_remote_function():
    assert ray.is_initialized()
    result = ray.get(check_interval.remote('84fbc502bc4e47cc4e49349392102b9f', 500000000, 500001000))
    assert result == (True, '050-0000100')
