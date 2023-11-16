from rest_framework import routers

from app_api_v2.viewsets import AuthorViewSet

router = routers.DefaultRouter()

router.register(
    "authors",
    AuthorViewSet,
    basename="api-v2-authors",
)

urlpatterns = router.urls
