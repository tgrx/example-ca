from rest_framework import routers

from app_api_v3.viewsets import BookViewSet

router = routers.DefaultRouter()

router.register(
    "books",
    BookViewSet,
    basename="api-v3-books",
)

urlpatterns = router.urls
