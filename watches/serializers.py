from rest_framework import serializers

from .models import Brand, Watch


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name"]


class WatchSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)

    class Meta:
        model = Watch
        fields = [
            "id",
            "title",
            "subtitle",
            "price",
            "link",
            "image",
            "location",
            "brand",
        ]


class BrandIdsSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all())
    )
