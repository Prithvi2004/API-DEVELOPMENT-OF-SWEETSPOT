#urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from django.conf.urls.static import static

from .views import *

router = DefaultRouter()
router.register(r"customers", CustomerViewSet)
router.register(r"cakes", CakeViewSet)
router.register(r"customizations", CakeCustomizationViewSet)
router.register(r"carts", CartViewSet)
router.register(r"orders", OrderViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

# Serve media files in development
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)