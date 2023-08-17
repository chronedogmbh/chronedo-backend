from django.contrib import messages
from django.shortcuts import redirect

import requests
from celery import shared_task
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import WatchFilter
from .models import Brand, Watch
from .serializers import BrandSerializer, WatchSerializer


@shared_task
def delete_sold_watches_task():
    watches = Watch.objects.all()
    for watch in watches:
        response = requests.get(watch.link)
        if response.status_code == 404 or response.status_code == 403:
            watch.delete()


def delete_sold_watches(request):
    delete_sold_watches_task.delay()
    messages.success(request, "Task to delete sold watches has been Executed.")
    return redirect("admin:index")


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]


class WatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Watch.objects.all().order_by("?").distinct()
    serializer_class = WatchSerializer
    permission_classes = [permissions.AllowAny]
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
