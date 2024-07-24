from rest_framework import serializers

from gymlog.gym.models import ExerciseLog
from gymlog.gym.models import SetLog
from gymlog.gym.models import Workout


class SetLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SetLog
        fields = ["id", "created", "modified", "order", "weight", "reps"]


class ExerciseLogSerializer(serializers.ModelSerializer):
    set_logs = SetLogSerializer(many=True)
    exercise_id = serializers.UUIDField()

    class Meta:
        model = ExerciseLog
        fields = ["id", "created", "modified", "order", "exercise_id", "set_logs"]


class WorkoutSerializer(serializers.ModelSerializer):
    exercise_logs = ExerciseLogSerializer(many=True)
    routine_id = serializers.UUIDField()

    """
    {
        "id": "0190e4ff-aa21-78f0-9ff8-15da21afda6d",
        "created": "2024-07-24T13:47:58.881405Z",
        "modified": "2024-07-24T13:47:58.881405Z",
        "start": null,
        "end": null,
        "duration": "00:45:00",
        "volume": 100.0,
        "routine_id": "0190e4ff-aa20-7942-a106-2a440c55cec5",
        "exercise_logs": [
            {
                "id": "0190e4ff-aa2b-7413-a352-573e66531d26",
                "created": "2024-07-24T13:47:58.891205Z",
                "modified": "2024-07-24T13:47:58.891205Z",
                "order": 1,
                "exercise_id": "0190e4ff-aa22-7770-9c73-6f826b68880e",
                "set_logs": [
                    {
                        "id": "0190e4ff-aa2d-7462-80f8-e4718f3cf83f",
                        "created": "2024-07-24T13:47:58.893291Z",
                        "modified": "2024-07-24T13:47:58.893291Z",
                        "order": 1,
                        "weight": 5.1,
                        "reps": 18
                    },
                    {
                        "id": "0190e4ff-aa30-7930-848e-eae88377efce",
                        "created": "2024-07-24T13:47:58.896214Z",
                        "modified": "2024-07-24T13:47:58.896214Z",
                        "order": 2,
                        "weight": 72.5,
                        "reps": 9
                    },
                    {
                        "id": "0190e4ff-aa31-7b21-9b5e-621d4262a227",
                        "created": "2024-07-24T13:47:58.897918Z",
                        "modified": "2024-07-24T13:47:58.897918Z",
                        "order": 3,
                        "weight": 9.5,
                        "reps": 14
                    }
                ]
            },
            {
                "id": "0190e4ff-aa2c-7b32-9673-c5a81f722b9b",
                "created": "2024-07-24T13:47:58.892160Z",
                "modified": "2024-07-24T13:47:58.892160Z",
                "order": 2,
                "exercise_id": "0190e4ff-aa29-7d61-84f0-6426d9c1c70f",
                "set_logs": [
                    {
                        "id": "0190e4ff-aa2f-7f40-9ca1-952233175609",
                        "created": "2024-07-24T13:47:58.895257Z",
                        "modified": "2024-07-24T13:47:58.895257Z",
                        "order": 1,
                        "weight": 95.7,
                        "reps": 4
                    },
                    {
                        "id": "0190e4ff-aa31-7b21-9b5e-6209fb205e52",
                        "created": "2024-07-24T13:47:58.897081Z",
                        "modified": "2024-07-24T13:47:58.897081Z",
                        "order": 2,
                        "weight": 41.1,
                        "reps": 19
                    },
                    {
                        "id": "0190e4ff-aa32-7033-8f95-2c32157f8324",
                        "created": "2024-07-24T13:47:58.898734Z",
                        "modified": "2024-07-24T13:47:58.898734Z",
                        "order": 3,
                        "weight": 38.1,
                        "reps": 2
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
            "start",
            "end",
            "duration",
            "volume",
            "routine_id",
            "exercise_logs",
        ]

    def update(self, workout: Workout, validated_data):
        exercise_logs_data = validated_data.pop("exercise_logs", [])
        routine_id = validated_data.pop("routine_id", None)
        if routine_id:
            workout.routine_id = routine_id

        workout = super().update(workout, validated_data)

        # Delete old exercise logs and their related set logs
        workout.exercise_logs.all().delete()

        # Create new exercise logs and set logs
        for exercise_log_data in exercise_logs_data:
            set_logs_data = exercise_log_data.pop("set_logs", [])
            exercise_log = ExerciseLog.objects.create(
                workout=workout,
                **exercise_log_data,
            )

            for set_log_data in set_logs_data:
                SetLog.objects.create(exercise_log=exercise_log, **set_log_data)

        return workout
