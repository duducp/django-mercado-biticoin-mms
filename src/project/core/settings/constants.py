########
# TIME #
########
SECONDS = 1
MINUTES = 60 * SECONDS
HOURS = 60 * MINUTES
DAYS = 24 * HOURS
WEEKS = 7 * DAYS


############
# BACKENDS #
############

# CANDLES
CANDLE_FAKE = 'project.backends.extensions.fake.candle.FakeCandleBackend'
CANDLE_MERCADOBITCOIN = 'project.backends.extensions.mercadobitcoin.backend.MercadoBitcoinCandleBackend' # noqa
