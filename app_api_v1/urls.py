from rest_framework import routers

from app_api_v1.viewsets import AuthorViewSet

router = routers.DefaultRouter()

router.register(
    "authors",
    AuthorViewSet,
    basename="api-v1-authors",
)

urlpatterns = router.urls
