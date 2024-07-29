from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet, ManageUserView

router = DefaultRouter()
router.register("users", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("me/", ManageUserView.as_view(), name="me"),
]

app_name = "users"
