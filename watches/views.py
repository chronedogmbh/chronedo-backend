from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import WatchFilter
from .models import Brand, Watch
from .serializers import BrandSerializer, WatchSerializer


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticated]


class WatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Watch.objects.all().order_by("?").distinct()
    serializer_class = WatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = WatchFilter

    def get_serializer_class(self):
        if self.action == "toggle_like":
            return serializers.Serializer
        else:
            return WatchSerializer

    @action(detail=True, methods=["post"], url_path="toggle-like")
    def toggle_like(self, request, pk=None):
        watch = self.get_object()
        if request.user in watch.likes.all():
            watch.likes.remove(request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            watch.likes.add(request.user)
            return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="liked-watches")
    def liked_watches(self, request, pk=None):
        watches = Watch.objects.filter(likes=request.user)
        serializer = WatchSerializer(watches, many=True)
        return Response(serializer.data)
