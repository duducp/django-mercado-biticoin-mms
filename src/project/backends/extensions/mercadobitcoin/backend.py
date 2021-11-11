from typing import List

import structlog
from aiohttp_retry import RandomRetry, RetryClient
from orjson import orjson
from simple_settings import settings

from project.backends.candle.backend import CandleBackend
from project.backends.candle.schemas import CandleSchema

logger = structlog.get_logger()
EXTENSION_CONFIG_CANDLE = settings.EXTENSIONS_CONFIG['candle']['mercadobitcoin'] # noqa


class MercadoBitcoinCandleBackend(CandleBackend):
    id = 'mercadobitcoin'

    async def _get_candles(
        self,
        pair: str,
        from_timestamp: int,
        to_timestamp: int,
        precision: str
    ) -> List[CandleSchema]:
        url = EXTENSION_CONFIG_CANDLE['url'].format(pair=pair)
        params = {
            'from': from_timestamp,
            'to': to_timestamp,
            'precision': precision
        }
        timeout = EXTENSION_CONFIG_CANDLE['timeout']
        max_retries = EXTENSION_CONFIG_CANDLE['max_retries']

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
            )
        ) as client:
            async with client.get(
                url=url,
                params=params,
                timeout=timeout
            ) as response:
                data = await response.text()
                data_json = orjson.loads(data)
                data_schema = CandleSchema.from_list(
                    items=data_json['candles']
                )
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
