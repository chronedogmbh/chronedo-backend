from django.contrib import admin

from .models import Brand, Watch


class BrandAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )
    search_fields = ("name",)


class WatchAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "price",
        "brand",
        "location",
    )
    search_fields = ("title", "subtitle", "brand__name", "location")
    list_filter = ("brand", "location")


admin.site.register(Brand, BrandAdmin)
admin.site.register(Watch, WatchAdmin)
