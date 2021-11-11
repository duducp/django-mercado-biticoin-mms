from decimal import Decimal
from http import HTTPStatus
from unittest.mock import patch
from urllib.parse import urlencode

import pytest
from model_bakery import baker


@pytest.mark.django_db
class TestRetrieveIndicatorMmsView:

    @pytest.fixture()
    def simple_moving_average(self):
        yield baker.make(
            'SimpleMovingAverage',
            precision='1d',
            pair='BRLBTC',
            mms_20=Decimal('201108.2404745000'),
            mms_50=Decimal('258627.0329508000'),
            mms_200=Decimal('229149.8719421000'),
            timestamp=1623034799
        )

    @pytest.fixture
    def mock_cache(self):
        with patch(
            'project.indicators.mms.views.cache'
        ) as mock_cache:
            yield mock_cache

    @pytest.mark.parametrize('_range,_mms', [
        (20, 201108.2404745),
        (50, 258627.0329508),
        (200, 229149.8719421),
    ])
    def test_should_validate_status_code_and_body_on_success_when_route_is_called(  # noqa
        self,
        client,
        simple_moving_average,
        mock_cache,
        _range,
        _mms
    ):
        mock_cache.get.return_value = None
        params = {
            'from': 1622862000,
            'to': 1623034799,
            'range': _range,
            'precision': '1d'
        }
        query_string = urlencode(params)
        path = f'/v1/indicators/BRLBTC/mms?{query_string}'

        response = client.get(path)
        data = response.json()

        assert response.status_code == HTTPStatus.OK
        assert data == [{'timestamp': 1623034799, 'mms': _mms}]
        mock_cache.get.assert_called_once_with(
            f'mms_retrieve_BRLBTC_1d_{_range}_1622862000_1623034799'
        )
        mock_cache.set.assert_called_once_with(
            key=f'mms_retrieve_BRLBTC_1d_{_range}_1622862000_1623034799',
            value=[
                {'mms': Decimal(f'{_mms}'), 'timestamp': 1623034799}
            ],
            timeout=600
        )

    @patch(
        'project.indicators.mms.views.get_simple_moving_average_variations',
        side_effect=Exception
    )
    def test_should_validate_status_code_and_body_when_an_exception_occurs(
        self,
        mock_helper,
        client,
        simple_moving_average
    ):
        query_string = urlencode({
            'from': 1622862000,
            'to': 1623034799,
            'range': 20,
            'precision': '1d'
        })
        path = f'/v1/indicators/BRLBTC/mms?{query_string}'

        response = client.get(path)
        data = response.json()

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert data == {
            'detail': 'An internal error occurred while making the request.'
        }

    def test_should_validate_status_code_and_body_when_query_params_is_invalid(
        self,
        client,
        simple_moving_average
    ):
        params = {
            'from': 'dffs',
            'to': 'dsfdsf',
            'range': 30,
            'precision': '1d'
        }
        query_string = urlencode(params)
        path = f'/v1/indicators/BRLBTC/mms?{query_string}'

        response = client.get(path)
        data = response.json()

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert data == {
            'detail': [
                {'loc': ['query', 'from'], 'msg': 'value is not a valid integer', 'type': 'type_error.integer'},  # noqa
                {'loc': ['query', 'to'], 'msg': 'value is not a valid integer', 'type': 'type_error.integer'},  # noqa
                {'loc': ['query', 'range'], 'msg': 'value is not a valid enumeration member; permitted: 20, 50, 200', 'type': 'type_error.enum', 'ctx': {'enum_values': [20, 50, 200]}}  # noqa
            ]
        }

    def test_should_validate_status_code_and_body_when_query_params_is_required(  # noqa
        self,
        client,
        simple_moving_average
    ):
        response = client.get('/v1/indicators/BRLBTC/mms')
        data = response.json()

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert data == {
            'detail': [
                {'loc': ['query', 'from'], 'msg': 'field required', 'type': 'value_error.missing'},  # noqa
                {'loc': ['query', 'range'], 'msg': 'field required', 'type': 'value_error.missing'}  # noqa
            ]
        }

    def test_should_validate_status_code_and_body_when_route_is_invalid(
        self,
        client,
        simple_moving_average
    ):
        response = client.get('/v1/indicators/BRLBTC/mm/')
        data = response.json()

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert data == {
            'detail': 'The accessed route does not exist.'
        }

    def test_should_validate_whether_the_date_range_is_not_greater_than_365_days(  # noqa
        self,
        client,
        simple_moving_average,
    ):
        params = {
            'from': 1591326000,
            'to': 1623034799,
            'range': 20,
            'precision': '1d'
        }
        query_string = urlencode(params)
        path = f'/v1/indicators/BRLBTC/mms?{query_string}'

        response = client.get(path)
        data = response.json()

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert data == {
            'detail': [
                {'loc': ['query', 'from'], 'msg': 'Start date cannot be longer than 365 days', 'type': 'value_error'}  # noqa
            ]
        }
