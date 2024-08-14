from django.conf import settings
from django.db.models import CASCADE
from django.db.models import SET_NULL
from django.db.models import CharField
from django.db.models import DateTimeField
from django.db.models import DurationField
from django.db.models import FloatField
from django.db.models import ForeignKey
from django.db.models import ImageField
from django.db.models import PositiveIntegerField
from django.db.models import TextChoices
from django.db.models import TextField
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from multiselectfield import MultiSelectField

from gymlog.mixins import UUIDModel


class Exercise(TimeStampedModel, UUIDModel):
    class Equipments(TextChoices):
        NONE = "none", _("None")
        BARBELL = "barbell", _("Barbell")
        DUMBBELL = "dumbbell", _("Dumbbell")
        KETTLEBELL = "kettlebell", _("Kettlebell")
        MACHINE = "machine", _("Machine")
        PLATE = "plate", _("Plate")
        RESISTANCE_BAND = "resistance_band", _("Resistance Band")
        SUSPENSION = "suspension", _("Suspension")
        OTHER = "other", _("Other")

    class MuscleGroups(TextChoices):
        ABDOMINALS = "abdominals", _("Abdominals")
        ABDUCTORS = "abductors", _("Abductors")
        ADDUCTORS = "adductors", _("Adductors")
        BICEPS = "biceps", _("Biceps")
        LOWER_BACK = "lower_back", _("Lower Back")
        UPPER_BACK = "upper_back", _("Upper Back")
        CARDIO = "cardio", _("Cardio")
        CHEST = "chest", _("Chest")
        CALVES = "calves", _("Calves")
        FOREARMS = "forearms", _("Forearms")
        GLUTES = "glutes", _("Glutes")
        HAMSTRINGS = "hamstrings", _("Hamstrings")
        LATS = "lats", _("Lats")
        QUADRICEPS = "quadriceps", _("Quadriceps")
        SHOULDERS = "shoulders", _("Shoulders")
        TRICEPS = "triceps", _("Triceps")
        TRAPS = "traps", _("Traps")
        NECK = "neck", _("Neck")
        FULL_BODY = "full_body", _("Full Body")
        OTHER = "other", _("Other")

    class ExerciseTypes(TextChoices):
        WEIGHT_REPS = "weight_reps", _("Weight Reps")
        REPS_ONLY = "reps_only", _("Reps Only")
        WEIGHTED_BODYWEIGHT = "weighted_bodyweight", _("Weighted Bodyweight")
        ASSISTED_BODYWEIGHT = "assisted_bodyweight", _("Assisted Bodyweight")
        DURATION = "duration", _("Duration")
        WEIGHT_DURATION = "weight_duration", _("Weight & Duration")
        DISTANCE_DURATION = "distance_duration", _("Distance Duration")
        WEIGHT_DISTANCE = "weight_distance", _("Weight & Distance")
        BODYWEIGHT_REPS = "bodyweight_reps", _("Bodyweight Reps")
        BODYWEIGHT_ASSISTED_REPS = (
            "bodyweight_assisted_reps",
            _("Bodyweight Assisted Reps"),
        )
        SHORT_DISTANCE_WEIGHT = "short_distance_weight", _("Short Distance Weight")

    name = CharField(_("Name"), max_length=255)
    exercise_type = CharField(
        _("Exercise Type"),
        max_length=255,
        choices=ExerciseTypes.choices,
    )
    equipment = CharField(
        _("Equipment"),
        max_length=255,
        blank=True,
        choices=Equipments.choices,
    )
    primary_muscle_group = CharField(
        _("Primary muscle group"),
        max_length=255,
        choices=MuscleGroups.choices,
    )
    other_muscles = MultiSelectField(
        _("Other Muscles"),
        max_length=255,
        blank=True,
        choices=MuscleGroups.choices,
    )
    small_image = ImageField(
        _("Small Image"),
        upload_to="exercise_small_images/",
        blank=True,
        null=True,
    )
    large_image = ImageField(
        _("Large Image"),
        upload_to="exercise_large_images/",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "exercises"
        verbose_name = _("Exercise")
        verbose_name_plural = _("Exercises")

    def __str__(self):
        return f"{self.name} [ID={self.id}]"


class Routine(TimeStampedModel, UUIDModel):
    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name="routines",
    )
    name = CharField(_("Name"), max_length=255)

    class Meta:
        db_table = "routines"
        verbose_name = _("Routine")
        verbose_name_plural = _("Routines")

    def __str__(self):
        return f"{self.name} [ID={self.id}]"


class RoutineExercise(TimeStampedModel, UUIDModel):
    routine = ForeignKey(Routine, on_delete=CASCADE, related_name="routine_exercises")
    order = PositiveIntegerField(_("Order"))
    exercise = ForeignKey(Exercise, on_delete=CASCADE)
    rest_timer = DurationField(
        _("Rest Timer"),
        default="00:01:00",
        blank=True,
        null=True,
    )
    note = TextField(_("Note"), blank=True)

    class Meta:
        db_table = "routine_exercises"
        verbose_name = _("Routine Exercise")
        verbose_name_plural = _("Routine Exercises")
        unique_together = ("routine", "exercise")
        ordering = ["order"]

    def __str__(self):
        return f"#{self.order} [ID={self.id}]"


class RoutineSet(TimeStampedModel, UUIDModel):
    routine_exercise = ForeignKey(
        RoutineExercise,
        on_delete=CASCADE,
        related_name="routine_sets",
    )
    order = PositiveIntegerField(_("Order"))
    weight = FloatField(_("Weight"))
    reps = PositiveIntegerField(_("Reps"))

    class Meta:
        db_table = "routine_sets"
        verbose_name = _("Routine Set")
        verbose_name_plural = _("Routine Sets")
        ordering = ["routine_exercise", "order"]
        unique_together = ("routine_exercise", "order")

    def __str__(self):
        return (
            f"#{self.order} - Weight: {self.weight}, Reps: {self.reps} [ID={self.id}]"
        )


class Workout(TimeStampedModel, UUIDModel):
    routine = ForeignKey(
        Routine,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name="workouts",
    )
    duration = DurationField(_("Duration"), blank=True, null=True)
    volume = FloatField(_("Volume"), blank=True, null=True, default=0.0)
    end = DateTimeField(_("End Time"), null=True, blank=True)

    class Meta:
        db_table = "workouts"
        verbose_name = _("Workout")
        verbose_name_plural = _("Workouts")
        ordering = ["-created"]

    def __str__(self):
        return f"Duration: {self.duration}, Volume: {self.volume} [ID={self.id}]"


class ExerciseLog(TimeStampedModel, UUIDModel):
    workout = ForeignKey(Workout, on_delete=CASCADE, related_name="exercise_logs")
    exercise = ForeignKey(Exercise, on_delete=CASCADE)
    order = PositiveIntegerField(_("Order"))

    class Meta:
        db_table = "exercise_logs"
        verbose_name = _("Exercise Log")
        verbose_name_plural = _("Exercise Logs")
        unique_together = ("workout", "order")
        ordering = ["order"]

    def __str__(self):
        return f"[ID={self.id}]"


class SetLog(TimeStampedModel, UUIDModel):
    exercise_log = ForeignKey(ExerciseLog, on_delete=CASCADE, related_name="set_logs")
    order = PositiveIntegerField(_("Order"))
    weight = FloatField(_("Weight"))
    reps = PositiveIntegerField(_("Reps"))
    end = DateTimeField(_("End Time"), null=True, blank=True)

    class Meta:
        db_table = "set_logs"
        verbose_name = _("Set Log")
        verbose_name_plural = _("Set Logs")
        ordering = ["order"]
        unique_together = ("exercise_log", "order")

    def __str__(self):
        return (
            f"#{self.order} - Weight: {self.weight}, Reps: {self.reps} [ID={self.id}]"
        )
