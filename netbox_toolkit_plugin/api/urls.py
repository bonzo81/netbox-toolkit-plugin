from netbox.api.routers import NetBoxRouter

from .views import CommandLogViewSet, CommandViewSet
from .views.credential_sets import DeviceCredentialSetViewSet

app_name = "netbox_toolkit_plugin"

router = NetBoxRouter()
router.register("commands", CommandViewSet)
router.register("command-logs", CommandLogViewSet)
router.register(
    "credential-sets", DeviceCredentialSetViewSet, basename="devicecredentialset"
)

urlpatterns = router.urls
