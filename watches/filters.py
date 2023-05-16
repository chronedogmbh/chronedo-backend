from django_filters import rest_framework as filters

from .models import Watch


class WatchFilter(filters.FilterSet):
    brands = filters.CharFilter(
        method="filter_by_brands", label="Brand IDs separated by comma"
    )
    price__gte = filters.NumberFilter(field_name="price", lookup_expr="gte")
    price__lte = filters.NumberFilter(field_name="price", lookup_expr="lte")
    location = filters.CharFilter(field_name="location", lookup_expr="icontains")

    class Meta:
        model = Watch
        fields = ["brands", "price__gte", "price__lte", "location"]

    def filter_by_brands(self, queryset, name, value):
        values = value.split(",")
        return queryset.filter(brand__in=values)
