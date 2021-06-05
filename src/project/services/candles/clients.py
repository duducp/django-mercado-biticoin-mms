import asyncio
from typing import List
from urllib.parse import urljoin

import orjson
import structlog
from aiohttp import ClientError, ClientResponseError
from aiohttp_retry import RandomRetry, RetryClient
from simple_settings import settings

from project.services.candles.exceptions import (
    ServiceCandleClientException,
    ServiceCandleException,
    ServiceCandleRequestClientException,
    ServiceCandleTimeoutException
)
from project.services.candles.schemas import CandleSchema

logger = structlog.get_logger()

CANDLE_SETTINGS = settings.SERVICES['candles']


async def get_candles(
    pair: str,
    from_timestamp: int,
    to_timestamp: int,
    precision: str = '1d'
) -> List[CandleSchema]:
    """
    Make a request in the Candles API to filter a pair by date range
    """

    try:
        url = urljoin(CANDLE_SETTINGS['url'], f'{pair}/candle')
        params = {
            'from': from_timestamp,
            'to': to_timestamp,
            'precision': precision
        }
        timeout = CANDLE_SETTINGS['timeout']
        max_retries = CANDLE_SETTINGS['max_retries']

        logger.info(
            'Starting request for candles',
            url=url,
            params=params,
            timeout=timeout,
            max_retries=max_retries,
        )

        async with RetryClient(
            logger=logger,
            raise_for_status=True,
            retry_options=RandomRetry(
                attempts=max_retries,
                max_timeout=timeout
            ),
        ) as client:
            async with client.get(
                url=url,
                params=params,
                timeout=CANDLE_SETTINGS['timeout'],
            ) as response:
                data = await response.text()
                data_json = orjson.loads(data)

                data_schema = [
                    CandleSchema.from_dict(candle)
                    for candle in data_json['candles']
                ]

                data_schema_sorted = sorted(
                    data_schema,
                    key=lambda candle: candle.timestamp,
                    reverse=True
                )

                logger.info(
                    'Finished request for candles',
                    status_code=response.status,
                    response=data_json,
                )

        return data_schema_sorted

    except ClientResponseError as exc:
        raise ServiceCandleRequestClientException(
            'Client request error when requesting the Candles API',
            status_code=exc.status
        ) from exc

    except ClientError as exc:
        raise ServiceCandleClientException(
            'Client error when requesting the Candles API',
        ) from exc

    except asyncio.TimeoutError as exc:
        raise ServiceCandleTimeoutException(
            'Timeout in the Candles API request'
        ) from exc

    except Exception as exc:
        raise ServiceCandleException(
            'Generic error when making a request to the Candles API'
        ) from exc
