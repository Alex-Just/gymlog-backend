from django.db import transaction
from rest_framework import serializers

from gymlog.gym.models import ExerciseLog
from gymlog.gym.models import Routine
from gymlog.gym.models import RoutineExercise
from gymlog.gym.models import RoutineSet
from gymlog.gym.models import SetLog
from gymlog.gym.models import Workout


class SetLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SetLog
        fields = ["id", "created", "modified", "order", "weight", "reps", "end"]


class ExerciseLogSerializer(serializers.ModelSerializer):
    set_logs = SetLogSerializer(many=True)
    exercise_id = serializers.UUIDField()

    class Meta:
        model = ExerciseLog
        fields = ["id", "created", "modified", "order", "exercise_id", "set_logs"]


class WorkoutSerializer(serializers.ModelSerializer):
    exercise_logs = ExerciseLogSerializer(many=True)
    routine_id = serializers.UUIDField()

    """ E.g.
    {
        "id": "0190e5af-3cc2-7293-b925-eaaa928569d5",
        "created": "2024-07-24T16:59:45.218940Z",
        "modified": "2024-07-24T16:59:45.326588Z",
        "start": null,
        "end": null,
        "duration": "01:30:00",
        "volume": 300.0,
        "routine_id": "0190e5af-3cc2-7293-b925-ea9fa315c6db",
        "exercise_logs": [
            {
                "id": "0190e5af-3d30-7b53-b0d9-071e08831a2d",
                "created": "2024-07-24T16:59:45.328165Z",
                "modified": "2024-07-24T16:59:45.328165Z",
                "order": 1,
                "exercise_id": "0190e5af-3cc4-7360-bbfb-964e3f47814a",
                "set_logs": [
                    {
                        "id": "0190e5af-3d30-7b53-b0d9-0720641c848c",
                        "created": "2024-07-24T16:59:45.328408Z",
                        "modified": "2024-07-24T16:59:45.328408Z",
                        "order": 1,
                        "weight": 60.0,
                        "reps": 12,
                        "end": null
                    }
                ]
            },
            {
                "id": "0190e5af-3d30-7b53-b0d9-0738fc07abad",
                "created": "2024-07-24T16:59:45.328608Z",
                "modified": "2024-07-24T16:59:45.328608Z",
                "order": 2,
                "exercise_id": "0190e5af-3ccf-7aa2-b667-157f97c5cde7",
                "set_logs": [
                    {
                        "id": "0190e5af-3d30-7b53-b0d9-074688c9a354",
                        "created": "2024-07-24T16:59:45.328787Z",
                        "modified": "2024-07-24T16:59:45.328787Z",
                        "order": 1,
                        "weight": 70.0,
                        "reps": 15,
                        "end": null
                    }
                ]
            }
        ]
    }
    """

    class Meta:
        model = Workout
        fields = [
            "id",
            "created",
            "modified",
            "end",
            "duration",
            "volume",
            "routine_id",
            "exercise_logs",
        ]

    @transaction.atomic
    def update(self, workout: Workout, validated_data):
        new_exercise_logs = validated_data.pop("exercise_logs", [])
        routine_id = validated_data.pop("routine_id", None)
        if routine_id:
            workout.routine_id = routine_id

        workout = super().update(workout, validated_data)

        # Delete old exercise logs and their related set logs
        workout.exercise_logs.all().delete()

        # Create new exercise logs and set logs
        for new_exercise_log in new_exercise_logs:
            new_set_logs = new_exercise_log.pop("set_logs", [])
            exercise_log = ExerciseLog.objects.create(
                workout=workout,
                **new_exercise_log,
            )
            for set_log_data in new_set_logs:
                SetLog.objects.create(exercise_log=exercise_log, **set_log_data)

        return workout


class RoutineSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutineSet
        fields = ["id", "created", "modified", "order", "weight", "reps"]


class RoutineExerciseSerializer(serializers.ModelSerializer):
    routine_sets = RoutineSetSerializer(many=True)
    exercise_id = serializers.UUIDField()

    class Meta:
        model = RoutineExercise
        fields = [
            "id",
            "created",
            "modified",
            "order",
            "exercise_id",
            "rest_timer",
            "note",
            "routine_sets",
            "exercise_id",
        ]


class RoutineSerializer(serializers.ModelSerializer):
    routine_exercises = RoutineExerciseSerializer(many=True)

    """E.g.
    {
        "id": "0190e5f0-d9ed-78d2-940f-7945548a552b",
        "created": "2024-07-24T18:11:25.293236Z",
        "modified": "2024-07-24T18:11:25.293236Z",
        "name": "TestRoutine1",
        "routine_exercises": [
            {
                "id": "0190e5f0-d9f5-72f1-9854-58f9d5479669",
                "created": "2024-07-24T18:11:25.301404Z",
                "modified": "2024-07-24T18:11:25.301404Z",
                "order": 1,
                "exercise_id": "0190e5f0-d9ee-7ef2-a715-0d1d87cbe3ac",
                "rest_timer": "00:01:00",
                "note": "",
                "routine_sets": [
                    {
                        "id": "0190e5f0-d9f6-7393-8cd7-89c5603221c7",
                        "created": "2024-07-24T18:11:25.302524Z",
                        "modified": "2024-07-24T18:11:25.302524Z",
                        "order": 1,
                        "weight": 87.5,
                        "reps": 9
                    }
                ]
            }
        ]
    }
    """

    class Meta:
        model = Routine
        fields = ["id", "created", "modified", "name", "routine_exercises"]

    @transaction.atomic
    def create(self, validated_data):
        new_routine_exercises = validated_data.pop("routine_exercises")
        user = self.context["request"].user
        routine = Routine.objects.create(user=user, **validated_data)

        for new_routine_exercise in new_routine_exercises:
            new_routine_sets = new_routine_exercise.pop("routine_sets")
            routine_exercise = RoutineExercise.objects.create(
                routine=routine,
                **new_routine_exercise,
            )
            for new_routine_set in new_routine_sets:
                RoutineSet.objects.create(
                    routine_exercise=routine_exercise,
                    **new_routine_set,
                )

        return routine

    @transaction.atomic
    def update(self, instance, validated_data):
        new_routine_exercises = validated_data.pop("routine_exercises")

        instance = super().update(instance, validated_data)

        # Delete old routine exercises and their related routine sets
        instance.routine_exercises.all().delete()

        # Create new routine exercises and routine sets
        for new_routine_exercise in new_routine_exercises:
            new_routine_sets = new_routine_exercise.pop("routine_sets")
            routine_exercise = RoutineExercise.objects.create(
                routine=instance,
                **new_routine_exercise,
            )
            for new_routine_set in new_routine_sets:
                RoutineSet.objects.create(
                    routine_exercise=routine_exercise,
                    **new_routine_set,
                )

        return instance
