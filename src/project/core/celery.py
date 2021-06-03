from celery import Celery

from manage import set_settings_module

set_settings_module()

app = Celery('project')
app.config_from_object('simple_settings:settings', namespace='CELERY')
app.autodiscover_tasks(related_name='tasks')
app.conf.broker_transport_options = {
    'queue_order_strategy': 'priority',
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
