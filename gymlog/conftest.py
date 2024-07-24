import pytest
from rest_framework.test import APIClient

from gymlog.gym.models import Routine
from gymlog.gym.models import Workout
from gymlog.gym.tests.factories import ExerciseFactory
from gymlog.gym.tests.factories import ExerciseLogFactory
from gymlog.gym.tests.factories import RoutineExerciseFactory
from gymlog.gym.tests.factories import RoutineFactory
from gymlog.gym.tests.factories import RoutineSetFactory
from gymlog.gym.tests.factories import SetLogFactory
from gymlog.users.models import User
from gymlog.users.tests.factories import UserFactory


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture()
def user(db) -> User:
    return UserFactory()


@pytest.fixture()
def workout(user: User) -> Workout:
    routine = Routine.objects.create(user=user, name="Test Routine")
    workout = Workout.objects.create(
        routine=routine,
        duration="00:45:00",
        volume=100.0,
    )

    exercise1 = ExerciseFactory(name="Exercise 1")
    exercise2 = ExerciseFactory(name="Exercise 2")

    exercise_log1 = ExerciseLogFactory(workout=workout, exercise=exercise1, order=1)
    exercise_log2 = ExerciseLogFactory(workout=workout, exercise=exercise2, order=2)

    for i in range(3):
        SetLogFactory(exercise_log=exercise_log1, order=i + 1)
        SetLogFactory(exercise_log=exercise_log2, order=i + 1)
    return workout


@pytest.fixture()
def routine(user: User) -> Routine:
    routine = RoutineFactory(user=user)
    routine_exercise = RoutineExerciseFactory(routine=routine, order=1)
    for i in range(3):
        RoutineSetFactory(routine_exercise=routine_exercise, order=i + 1)
    return routine
