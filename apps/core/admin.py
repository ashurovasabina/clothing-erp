from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ImportExportModelAdmin
from .models import Currency


class BaseAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    """Barcha admin modellari uchun asosiy admin klass"""
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if 'id' in fields:
            fields.remove('id')
        return fields


@admin.register(Currency)
class CurrencyAdmin(BaseAdmin):
    list_display = ('code', 'name', 'symbol', 'is_default')
    list_filter = ('is_default',)
    search_fields = ('code', 'name')
