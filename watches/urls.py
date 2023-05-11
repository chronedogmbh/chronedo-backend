from rest_framework.routers import DefaultRouter

from .views import BrandViewSet, WatchViewSet

router = DefaultRouter()
router.register("brands", BrandViewSet, basename="brand")
router.register("watches", WatchViewSet, basename="watch")


urlpatterns = router.urls
