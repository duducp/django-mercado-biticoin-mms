from ninja import Router

from project.indicators.mms.views import router as mms_router

router = Router()
router.add_router('/', mms_router, tags=['Simple Moving Average'])
