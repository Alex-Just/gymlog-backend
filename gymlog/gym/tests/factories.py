from factory import Faker
from factory import SubFactory
from factory.django import DjangoModelFactory

from gymlog.gym.models import Exercise
from gymlog.gym.models import ExerciseLog
from gymlog.gym.models import Routine
from gymlog.gym.models import RoutineExercise
from gymlog.gym.models import RoutineSet
from gymlog.gym.models import SetLog
from gymlog.gym.models import Workout
from gymlog.users.tests.factories import UserFactory


class ExerciseFactory(DjangoModelFactory):
    name = Faker("word")
    exercise_type = Faker(
        "random_element",
        elements=[choice[0] for choice in Exercise.ExerciseTypes.choices],
    )
    equipment = Faker(
        "random_element",
        elements=[choice[0] for choice in Exercise.Equipments.choices],
    )
    primary_muscle_group = Faker(
        "random_element",
        elements=[choice[0] for choice in Exercise.MuscleGroups.choices],
    )

    class Meta:
        model = Exercise
        django_get_or_create = ["name"]


class RoutineFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    name = Faker("word")

    class Meta:
        model = Routine
        django_get_or_create = ["name"]


class RoutineExerciseFactory(DjangoModelFactory):
    routine = SubFactory(RoutineFactory)
    exercise = SubFactory(ExerciseFactory)
    order = Faker("random_int", min=1, max=10)

    class Meta:
        model = RoutineExercise
        django_get_or_create = ["routine", "exercise", "order"]


class RoutineSetFactory(DjangoModelFactory):
    routine_exercise = SubFactory(RoutineExerciseFactory)
    order = Faker("random_int", min=1, max=10)
    weight = Faker("pyfloat", left_digits=2, right_digits=1, positive=True)
    reps = Faker("random_int", min=1, max=20)

    class Meta:
        model = RoutineSet
        django_get_or_create = ["routine_exercise", "order"]


class WorkoutFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    routine = SubFactory(RoutineFactory)
    duration = Faker("time_delta")
    volume = Faker("pyfloat", left_digits=2, right_digits=1, positive=True)

    class Meta:
        model = Workout
        django_get_or_create = ["user", "routine"]


class ExerciseLogFactory(DjangoModelFactory):
    workout = SubFactory(WorkoutFactory)
    exercise = SubFactory(ExerciseFactory)
    order = Faker("random_int", min=1, max=10)

    class Meta:
        model = ExerciseLog
        django_get_or_create = ["workout", "exercise", "order"]


class SetLogFactory(DjangoModelFactory):
    exercise_log = SubFactory(ExerciseLogFactory)
    order = Faker("random_int", min=1, max=10)
    weight = Faker("pyfloat", left_digits=2, right_digits=1, positive=True)
    reps = Faker("random_int", min=1, max=20)

    class Meta:
        model = SetLog
        django_get_or_create = ["exercise_log", "order"]
