from http import HTTPStatus

import pytest


class TestRetrieveTicketsView:

    @pytest.mark.asyncio
    async def test_should_validate_status_code_and_body_on_success_when_route_is_called(  # noqa
        self,
        async_client
    ):
        response = await async_client.get(path='/v1/tickets/')
        data = response.json()

        assert response.status_code == HTTPStatus.OK
        assert data == {'message': 'Hello world'}


class TestCreateTicketsView:

    @pytest.mark.asyncio
    async def test_should_validate_status_code_and_body_on_success_when_route_is_called(  # noqa
        self,
        async_client
    ):
        response = await async_client.post(
            path='/v1/tickets/',
            data={'message': 'Hello world'},
            content_type='application/json'
        )
        data = response.json()

        assert response.status_code == HTTPStatus.OK
        assert data == {'message': 'Hello world'}

    @pytest.mark.asyncio
    async def test_should_validate_status_code_and_body_on_payload_invalid_when_route_is_called(  # noqa
        self,
        async_client
    ):
        response = await async_client.post(
            path='/v1/tickets/',
            data=None,
            content_type='application/json'
        )
        data = response.json()

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert data == {
            'detail': [{
                'loc': ['body', 'payload', 'message'],
                'msg': 'field required',
                'type': 'value_error.missing'
            }]
        }
