from project.apps.indicators.mms.apps import MmsConfig


class TestApps:
    def test_should_be_successful_when_application_name_is_as_expected(self):
        assert MmsConfig.name == 'project.apps.indicators.mms'
        assert MmsConfig.verbose_name == 'Simple Moving Average'
