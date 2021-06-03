from django.test import AsyncClient, Client

import pytest


@pytest.fixture()
def async_client():
    """A Django async test client instance."""
    client = AsyncClient()
    yield client


@pytest.fixture()
def client():
    """A Django test client instance."""
    client = Client()
    yield client
