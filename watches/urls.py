from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import BrandViewSet, WatchViewSet, delete_sold_watches

router = DefaultRouter()
router.register("brands", BrandViewSet, basename="brand")
router.register("watches", WatchViewSet, basename="watch")


urlpatterns = router.urls
urlpatterns += [
    path("delete-sold-watches/", delete_sold_watches, name="delete-sold-watches"),
]
