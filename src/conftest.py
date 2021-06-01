from django.test import AsyncClient

import pytest


@pytest.fixture()
def async_client():
    """A Django async test client instance."""
    client = AsyncClient()
    yield client
