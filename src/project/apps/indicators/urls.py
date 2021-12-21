from ninja import Router

from project.apps.indicators.mms.views import router as mms_router

router = Router()
router.add_router('/', mms_router, tags=['Simple Moving Average'])
