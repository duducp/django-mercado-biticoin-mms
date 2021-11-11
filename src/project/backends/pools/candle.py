from ramos.pool import BackendPool


class CandlePool(BackendPool):
    """
    The name entered in backend_type must be the same name defined in settings:
    project.core.settings.base.POOL_OF_RAMOS

    1- Criar o backend em project.backends
    2- Criar o fake extension em project.backends.extensions.fake
    3- Criar a extension em project.backends.extensions
    4- Criar o pool em project.backends.pools
    5- Registrar o pool e as extensions em project.core.settings.base.POOL_OF_RAMOS
    """
    backend_type = 'candle'
