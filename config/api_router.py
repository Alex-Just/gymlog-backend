from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from gymlog.gym.api.views import RoutineViewSet
from gymlog.gym.api.views import SetLogViewSet
from gymlog.gym.api.views import WorkoutViewSet
from gymlog.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("workouts", WorkoutViewSet, basename="workout")
router.register(r"routines", RoutineViewSet)
router.register(
    r"workouts/(?P<workout_uuid>[^/.]+)/exercises/(?P<exercise_order>\d+)/sets",
    SetLogViewSet,
    basename="setlog",
)

app_name = "api"
urlpatterns = router.urls
