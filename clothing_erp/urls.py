from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy'})

urlpatterns = [
    # Non-i18n patterns
    path('i18n/', include('django.conf.urls.i18n')),  # This is for language switching
    path('health/', health_check, name='health_check'),
]

# Tarjima qilinadigan URL'lar
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),  # This should point to dashboard as home
    path('inventory/', include('apps.inventory.urls')),
    path('sales/', include('apps.sales.urls')),
    path('purchase/', include('apps.purchase.urls')),
    path('finance/', include('apps.finance.urls')),
    path('hr/', include('apps.hr.urls')),
    path('settings/', include('apps.settings.urls')),
    prefix_default_language=True
)

# Media va static fayllar
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)