from rest_framework import serializers

from .models import Brand, Watch


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name"]


class WatchSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()

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
            "is_liked",
        ]

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request:
            return request.user in obj.likes.all()
        return False
