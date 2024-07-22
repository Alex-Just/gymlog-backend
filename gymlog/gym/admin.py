from django.contrib import admin

from gymlog.mixins import GeneralModelAdmin

from .models import Exercise
from .models import ExerciseLog
from .models import Routine
from .models import RoutineExercise
from .models import RoutineSet
from .models import SetLog
from .models import Workout


@admin.register(Exercise)
class ExerciseAdmin(GeneralModelAdmin):
    list_display = ("name", "exercise_type", "equipment", "primary_muscle_group")
    search_fields = ("name", "exercise_type", "equipment", "primary_muscle_group")
    list_filter = ("exercise_type", "equipment", "primary_muscle_group")
    ordering = ("name",)


@admin.register(Routine)
class RoutineAdmin(GeneralModelAdmin):
    list_display = ("name", "user")
    search_fields = ("name", "user__email")
    list_select_related = ("user",)


@admin.register(RoutineExercise)
class RoutineExerciseAdmin(GeneralModelAdmin):
    list_display = ("routine", "order", "exercise", "order", "rest_timer")
    search_fields = ("routine__name", "exercise__name", "routine__user__email")
    list_filter = ("routine", "exercise")
    list_select_related = ("routine", "exercise")


@admin.register(RoutineSet)
class RoutineSetAdmin(GeneralModelAdmin):
    list_display = ("routine_exercise", "order", "weight", "reps")
    search_fields = (
        "routine_exercise__routine__name",
        "routine_exercise__exercise__name",
        "routine_exercise__routine__user__email",
    )
    list_filter = ("routine_exercise",)
    list_select_related = ("routine_exercise",)


@admin.register(Workout)
class WorkoutAdmin(GeneralModelAdmin):
    list_display = ("user", "routine", "start", "end", "duration", "volume")
    search_fields = ("user__username", "routine__name")
    list_filter = ("routine",)
    list_select_related = ("user", "routine")


@admin.register(ExerciseLog)
class ExerciseLogAdmin(GeneralModelAdmin):
    list_display = ("workout", "exercise", "order")
    search_fields = ("workout__user__username", "exercise__name")
    list_filter = ("exercise",)
    list_select_related = ("workout", "exercise")


@admin.register(SetLog)
class SetLogAdmin(GeneralModelAdmin):
    list_display = ("exercise_log", "order", "weight", "reps")
    search_fields = (
        "exercise_log__workout__user__username",
        "exercise_log__exercise__name",
    )
    list_select_related = ("exercise_log",)
