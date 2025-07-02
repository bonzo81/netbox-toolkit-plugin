from netbox.api.routers import NetBoxRouter
from .views import CommandViewSet, CommandLogViewSet

app_name = 'netbox_toolkit'

router = NetBoxRouter()
router.register('commands', CommandViewSet)
router.register('command-logs', CommandLogViewSet)

urlpatterns = router.urls
