import abc
import asyncio
from typing import List

from aiohttp import ClientError, ClientResponseError
from ramos.mixins import ThreadSafeCreateMixin

from project.backends.candle.exceptions import (
    CandleClientError,
    CandleError,
    CandleRequestClientError,
    CandleTimeoutError
)
from project.backends.candle.schemas import CandleSchema


class CandleBackend(
    ThreadSafeCreateMixin,
    metaclass=abc.ABCMeta
):
    @abc.abstractmethod
    def id(self):
        pass

    async def get_candles(
        self,
        pair: str,
        from_timestamp: int,
        to_timestamp: int,
        precision: str = '1d',
    ) -> List[CandleSchema]:
        try:
            return await self._get_candles(
                pair=pair,
                from_timestamp=from_timestamp,
                to_timestamp=to_timestamp,
                precision=precision,
            )

        except ClientResponseError as ex:
            raise CandleRequestClientError(
                'Client request error when requesting the Candles API',
                status_code=ex.status
            ) from ex

        except ClientError as exc:
            raise CandleClientError(
                'Client error when requesting the Candles API',
            ) from exc

        except asyncio.TimeoutError as exc:
            raise CandleTimeoutError(
                'Timeout in the Candles API request'
            ) from exc

        except Exception as ex:
            raise CandleError(
                'Generic error when making a request to the Candles API'
            ) from ex

    @abc.abstractmethod
    async def _get_candles(
        self,
        pair: str,
        from_timestamp: int,
        to_timestamp: int,
        precision: str,
    ) -> List[CandleSchema]:
        pass
