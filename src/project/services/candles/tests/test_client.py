from http import HTTPStatus
from urllib.parse import urlencode, urljoin

import pytest
from aiohttp import ClientError
from aioresponses import aioresponses
from asynctest import patch
from simple_settings import settings

from project.services.candles.clients import get_candles
from project.services.candles.exceptions import (
    ServiceCandleClientException,
    ServiceCandleException,
    ServiceCandleRequestClientException,
    ServiceCandleTimeoutException
)
from project.services.candles.schemas import CandleSchema

CANDLE_SETTINGS = settings.SERVICES['candles']


class TestGetCandles:
    @pytest.fixture
    def mock_logger(self):
        with patch(
            'project.services.candles.clients.logger'
        ) as logger:
            yield logger

    @pytest.fixture
    def pair(self):
        return 'BRLBTC'

    @pytest.fixture
    def params(self):
        return {
            'from': 1622592000,
            'to': 1622678400,
            'precision': '1d'
        }

    @pytest.fixture
    def url(self, pair, params):
        _params = {
            'from': params['from'],
            'to': params['to'],
            'precision': params['precision'],
        }
        query_string = urlencode(_params)
        return urljoin(CANDLE_SETTINGS['url'], f'{pair}/candle?{query_string}')

    @pytest.fixture
    def response_candles(self):
        return {
            'status_code': 100,
            'status_message': 'Success',
            'server_unix_timestamp': 1622840161,
            'candles': [
                {
                    'timestamp': 1622592000,
                    'open': 189998.44154,
                    'close': 191641.50495,
                    'high': 194430,
                    'low': 186620.81,
                    'volume': 96.4198213
                },
                {
                    'timestamp': 1622678400,
                    'open': 190806.74134,
                    'close': 198499.97958,
                    'high': 198542,
                    'low': 190000,
                    'volume': 72.58538109
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_should_validate_the_return_when_the_request_is_successful(
        self,
        mock_logger,
        response_candles,
        url,
        pair,
        params,
    ):
        with aioresponses() as session:
            session.get(
                url=url,
                status=HTTPStatus.OK,
                payload=response_candles,
            )
            response = await get_candles(
                pair=pair,
                from_timestamp=params['from'],
                to_timestamp=params['to'],
                precision=params['precision']
            )

            assert isinstance(response, list)
            assert len(response) == 2
            assert isinstance(response[0], CandleSchema)
            assert mock_logger.info.call_count == 2

    @pytest.mark.asyncio
    async def test_should_validate_the_return_when_a_request_client_error_occurs(  # noqa
        self,
        mock_logger,
        response_candles,
        url,
        pair,
        params,
    ):
        with aioresponses() as session:
            session.get(
                url=url,
                status=HTTPStatus.NOT_FOUND,
            )

            with pytest.raises(ServiceCandleRequestClientException) as exc:
                await get_candles(
                    pair=pair,
                    from_timestamp=params['from'],
                    to_timestamp=params['to'],
                    precision=params['precision']
                )

            assert (
                str(exc.value) ==
                'Client request error when requesting the Candles API'
            )
            assert mock_logger.info.call_count == 1

    @pytest.mark.asyncio
    async def test_should_validate_exception_when_client_error_occurs(
        self,
        mock_logger,
        response_candles,
        url,
        pair,
        params,
    ):
        with aioresponses() as session:
            session.get(
                url=url,
                exception=ClientError
            )

            with pytest.raises(ServiceCandleClientException) as exc:
                await get_candles(
                    pair=pair,
                    from_timestamp=params['from'],
                    to_timestamp=params['to'],
                    precision=params['precision']
                )

            assert (
                str(exc.value) ==
                'Client error when requesting the Candles API'
            )
            assert mock_logger.info.call_count == 1

    @pytest.mark.asyncio
    async def test_should_validate_the_return_when_a_request_timeout_error_occurs(  # noqa
        self,
        mock_logger,
        response_candles,
        url,
        pair,
        params,
    ):
        with aioresponses() as session:
            session.get(
                url=url,
                timeout=True,
            )

            with pytest.raises(ServiceCandleTimeoutException) as exc:
                await get_candles(
                    pair=pair,
                    from_timestamp=params['from'],
                    to_timestamp=params['to'],
                    precision=params['precision']
                )

            assert str(exc.value) == 'Timeout in the Candles API request'
            assert mock_logger.info.call_count == 1

    @pytest.mark.asyncio
    async def test_should_validate_the_return_when_a_exception_error_occurs(  # noqa
        self,
        mock_logger,
        response_candles,
        url,
        pair,
        params,
    ):
        with aioresponses() as session:
            session.get(
                url=url,
                exception=Exception
            )

            with pytest.raises(ServiceCandleException) as exc:
                await get_candles(
                    pair=pair,
                    from_timestamp=params['from'],
                    to_timestamp=params['to'],
                    precision=params['precision']
                )

            assert (
                str(exc.value) ==
                'Generic error when making a request to the Candles API'
            )
            assert mock_logger.info.call_count == 1
