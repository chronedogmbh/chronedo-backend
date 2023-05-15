from django_filters import rest_framework as filters

from .models import Watch


class WatchFilter(filters.FilterSet):
    brands = filters.CharFilter(
        method="filter_by_brands", label="Brand IDs separated by comma"
    )

    class Meta:
        model = Watch
        fields = ["brands"]

    def filter_by_brands(self, queryset, name, value):
        values = value.split(",")
        return queryset.filter(brand__in=values)
