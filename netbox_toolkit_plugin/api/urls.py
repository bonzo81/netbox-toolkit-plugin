from netbox.api.routers import NetBoxRouter

from .views import CommandLogViewSet, CommandViewSet

app_name = "netbox_toolkit_plugin"

router = NetBoxRouter()
router.register("commands", CommandViewSet)
router.register("command-logs", CommandLogViewSet)

urlpatterns = router.urls
