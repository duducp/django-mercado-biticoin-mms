from django.test import Client


class TestRetrievePingView:
    def test_should_validate_status_code_and_body_on_success_when_route_is_called(self):  # noqa
        client = Client()
        response = client.get(
            path='/ping/',
            format='json'
        )
        data = response.json()

        assert response.status_code == 200
        assert data['message']
        assert data['version']
        assert data['timestamp']
        assert data['host']
