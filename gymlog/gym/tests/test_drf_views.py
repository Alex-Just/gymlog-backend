from datetime import timedelta

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient

from gymlog.gym.models import Exercise
from gymlog.gym.models import Routine
from gymlog.gym.models import Workout
from gymlog.gym.tests.factories import ExerciseFactory
from gymlog.users.models import User

STATUS_OK = 200
STATUS_CREATED = 201
STATUS_NO_CONTENT = 204
STATUS_BAD_REQUEST = 400
STATUS_NOT_FOUND = 404

SMALL_GIF = (
    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80"
    b"\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00"
    b"\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
)


class TestWorkoutViewSet:
    def test_get_workout(self, user: User, api_client: APIClient, workout: Workout):
        exercise_logs_count = 2
        set_logs_count = 3

        api_client.force_authenticate(user=user)
        url = reverse("api:workout-detail", kwargs={"pk": workout.id})

        response = api_client.get(url)
        assert response.status_code == STATUS_OK

        workout_data = response.json()
        assert workout_data["routineId"] == str(workout.routine.id)
        assert len(workout_data["exerciseLogs"]) == exercise_logs_count

        for exercise_log in workout_data["exerciseLogs"]:
            assert len(exercise_log["setLogs"]) == set_logs_count

    def test_update_workout_invalid_data(
        self,
        user: User,
        api_client: APIClient,
        workout: Workout,
    ):
        api_client.force_authenticate(user=user)
        url = reverse("api:workout-detail", kwargs={"pk": workout.id})

        invalid_data = {
            "duration": "invalid_duration",
            "volume": "invalid_volume",
            "routine_id": "invalid_routine_id",
        }

        response = api_client.put(url, invalid_data, format="json")
        assert response.status_code == STATUS_BAD_REQUEST

    def test_update_workout(self, user: User, api_client: APIClient, workout: Workout):
        new_volume = 200.0
        new_weight = 50.0
        new_reps = 10

        api_client.force_authenticate(user=user)
        url = reverse("api:workout-detail", kwargs={"pk": workout.id})

        workout_end = (workout.created + timedelta(minutes=90)).isoformat()
        new_data = {
            "duration": "01:00:00",
            "volume": new_volume,
            "routine_id": str(workout.routine.id),
            "end": workout_end,
            "exercise_logs": [
                {
                    "order": 1,
                    "exercise_id": str(workout.exercise_logs.first().exercise.id),
                    "set_logs": [
                        {
                            "order": 1,
                            "weight": new_weight,
                            "reps": new_reps,
                        },
                    ],
                },
            ],
        }

        response = api_client.put(url, new_data, format="json")
        assert response.status_code == STATUS_OK

        workout.refresh_from_db()
        assert str(workout.duration) == "1:00:00"
        assert workout.end.isoformat() == workout_end
        assert workout.volume == pytest.approx(new_volume)

        exercise_log = workout.exercise_logs.first()
        set_log = exercise_log.set_logs.first()
        assert set_log.weight == pytest.approx(new_weight)
        assert set_log.reps == new_reps

    def test_update_workout_with_multiple_exercise_logs(
        self,
        user: User,
        api_client: APIClient,
        workout: Workout,
    ):
        new_volume = 300.0
        new_weight_1 = 60.0
        new_reps_1 = 12
        new_weight_2 = 70.0
        new_reps_2 = 15

        api_client.force_authenticate(user=user)
        url = reverse("api:workout-detail", kwargs={"pk": workout.id})

        new_data = {
            "duration": "01:30:00",
            "volume": new_volume,
            "routine_id": str(workout.routine.id),
            "exercise_logs": [
                {
                    "order": 1,
                    "exercise_id": str(workout.exercise_logs.first().exercise.id),
                    "set_logs": [
                        {
                            "order": 1,
                            "weight": new_weight_1,
                            "reps": new_reps_1,
                        },
                    ],
                },
                {
                    "order": 2,
                    "exercise_id": str(workout.exercise_logs.last().exercise.id),
                    "set_logs": [
                        {
                            "order": 1,
                            "weight": new_weight_2,
                            "reps": new_reps_2,
                        },
                    ],
                },
            ],
        }

        response = api_client.put(url, new_data, format="json")
        assert response.status_code == STATUS_OK

        workout.refresh_from_db()
        assert str(workout.duration) == "1:30:00"
        assert workout.volume == pytest.approx(new_volume)

        exercise_log_1 = workout.exercise_logs.get(order=1)
        set_log_1 = exercise_log_1.set_logs.first()
        assert set_log_1.weight == pytest.approx(new_weight_1)
        assert set_log_1.reps == new_reps_1

        exercise_log_2 = workout.exercise_logs.get(order=2)
        set_log_2 = exercise_log_2.set_logs.first()
        assert set_log_2.weight == pytest.approx(new_weight_2)
        assert set_log_2.reps == new_reps_2

    def test_update_workout_with_new_exercise_logs(
        self,
        user: User,
        api_client: APIClient,
        workout: Workout,
    ):
        new_volume = 250.0
        new_weight = 80.0
        new_reps = 20

        new_exercise = ExerciseFactory(name="New Exercise")

        api_client.force_authenticate(user=user)
        url = reverse("api:workout-detail", kwargs={"pk": workout.id})

        new_data = {
            "duration": "01:15:00",
            "volume": new_volume,
            "routine_id": str(workout.routine.id),
            "exercise_logs": [
                {
                    "order": 3,
                    "exercise_id": str(new_exercise.id),
                    "set_logs": [
                        {
                            "order": 1,
                            "weight": new_weight,
                            "reps": new_reps,
                        },
                    ],
                },
            ],
        }

        response = api_client.put(url, new_data, format="json")
        assert response.status_code == STATUS_OK

        workout.refresh_from_db()
        assert str(workout.duration) == "1:15:00"
        assert workout.volume == pytest.approx(new_volume)

        exercise_log = workout.exercise_logs.get(order=3)
        set_log = exercise_log.set_logs.first()
        assert set_log.weight == pytest.approx(new_weight)
        assert set_log.reps == new_reps

    def test_update_workout_with_existing_and_new_exercise_logs(
        self,
        user: User,
        api_client: APIClient,
        workout: Workout,
    ):
        new_volume = 220.0
        new_weight_1 = 55.0
        new_reps_1 = 11
        new_weight_2 = 75.0
        new_reps_2 = 17

        new_exercise = ExerciseFactory(name="Another New Exercise")

        api_client.force_authenticate(user=user)
        url = reverse("api:workout-detail", kwargs={"pk": workout.id})

        new_data = {
            "duration": "01:20:00",
            "volume": new_volume,
            "routine_id": str(workout.routine.id),
            "exercise_logs": [
                {
                    "order": 1,
                    "exercise_id": str(workout.exercise_logs.first().exercise.id),
                    "set_logs": [
                        {
                            "order": 1,
                            "weight": new_weight_1,
                            "reps": new_reps_1,
                        },
                    ],
                },
                {
                    "order": 3,
                    "exercise_id": str(new_exercise.id),
                    "set_logs": [
                        {
                            "order": 1,
                            "weight": new_weight_2,
                            "reps": new_reps_2,
                        },
                    ],
                },
            ],
        }

        response = api_client.put(url, new_data, format="json")
        assert response.status_code == STATUS_OK

        workout.refresh_from_db()
        assert str(workout.duration) == "1:20:00"
        assert workout.volume == pytest.approx(new_volume)

        exercise_log_1 = workout.exercise_logs.get(order=1)
        set_log_1 = exercise_log_1.set_logs.first()
        assert set_log_1.weight == pytest.approx(new_weight_1)
        assert set_log_1.reps == new_reps_1

        exercise_log_2 = workout.exercise_logs.get(order=3)
        set_log_2 = exercise_log_2.set_logs.first()
        assert set_log_2.weight == pytest.approx(new_weight_2)
        assert set_log_2.reps == new_reps_2

    def test_update_workout_with_multiple_sets(
        self,
        user: User,
        api_client: APIClient,
        workout: Workout,
    ):
        new_volume = 250.0
        new_weights = [60.0, 65.0, 70.0]
        new_reps = [12, 15, 18]

        api_client.force_authenticate(user=user)
        url = reverse("api:workout-detail", kwargs={"pk": workout.id})

        new_data = {
            "duration": "01:15:00",
            "volume": new_volume,
            "routine_id": str(workout.routine.id),
            "exercise_logs": [
                {
                    "order": 1,
                    "exercise_id": str(workout.exercise_logs.first().exercise.id),
                    "set_logs": [
                        {
                            "order": 1,
                            "weight": new_weights[0],
                            "reps": new_reps[0],
                        },
                        {
                            "order": 2,
                            "weight": new_weights[1],
                            "reps": new_reps[1],
                        },
                        {
                            "order": 3,
                            "weight": new_weights[2],
                            "reps": new_reps[2],
                        },
                    ],
                },
            ],
        }

        response = api_client.put(url, new_data, format="json")
        assert response.status_code == STATUS_OK

        workout.refresh_from_db()
        assert str(workout.duration) == "1:15:00"
        assert workout.volume == pytest.approx(new_volume)

        exercise_log = workout.exercise_logs.first()
        set_logs = exercise_log.set_logs.all()
        for i, set_log in enumerate(set_logs):
            assert set_log.weight == pytest.approx(new_weights[i])
            assert set_log.reps == new_reps[i]

    def test_update_workout_with_multiple_exercise_logs_and_sets(
        self,
        user: User,
        api_client: APIClient,
        workout: Workout,
    ):
        new_volume = 300.0
        new_weights_1 = [60.0, 65.0, 70.0]
        new_reps_1 = [12, 15, 18]
        new_weights_2 = [70.0, 75.0, 80.0]
        new_reps_2 = [18, 20, 22]

        api_client.force_authenticate(user=user)
        url = reverse("api:workout-detail", kwargs={"pk": workout.id})

        new_data = {
            "duration": "01:30:00",
            "volume": new_volume,
            "routine_id": str(workout.routine.id),
            "exercise_logs": [
                {
                    "order": 1,
                    "exercise_id": str(workout.exercise_logs.first().exercise.id),
                    "set_logs": [
                        {
                            "order": 1,
                            "weight": new_weights_1[0],
                            "reps": new_reps_1[0],
                        },
                        {
                            "order": 2,
                            "weight": new_weights_1[1],
                            "reps": new_reps_1[1],
                        },
                        {
                            "order": 3,
                            "weight": new_weights_1[2],
                            "reps": new_reps_1[2],
                        },
                    ],
                },
                {
                    "order": 2,
                    "exercise_id": str(workout.exercise_logs.last().exercise.id),
                    "set_logs": [
                        {
                            "order": 1,
                            "weight": new_weights_2[0],
                            "reps": new_reps_2[0],
                        },
                        {
                            "order": 2,
                            "weight": new_weights_2[1],
                            "reps": new_reps_2[1],
                        },
                        {
                            "order": 3,
                            "weight": new_weights_2[2],
                            "reps": new_reps_2[2],
                        },
                    ],
                },
            ],
        }

        response = api_client.put(url, new_data, format="json")
        assert response.status_code == STATUS_OK

        workout.refresh_from_db()
        assert str(workout.duration) == "1:30:00"
        assert workout.volume == pytest.approx(new_volume)

        exercise_log_1 = workout.exercise_logs.get(order=1)
        set_logs_1 = exercise_log_1.set_logs.all()
        for i, set_log in enumerate(set_logs_1):
            assert set_log.weight == pytest.approx(new_weights_1[i])
            assert set_log.reps == new_reps_1[i]

        exercise_log_2 = workout.exercise_logs.get(order=2)
        set_logs_2 = exercise_log_2.set_logs.all()
        for i, set_log in enumerate(set_logs_2):
            assert set_log.weight == pytest.approx(new_weights_2[i])
            assert set_log.reps == new_reps_2[i]

    def test_update_workout_with_new_exercise_logs_and_multiple_sets(
        self,
        user: User,
        api_client: APIClient,
        workout: Workout,
    ):
        new_volume = 220.0
        new_weight_1 = 55.0
        new_reps_1 = 11
        new_weight_2 = 75.0
        new_reps_2 = 17

        new_exercise = ExerciseFactory(name="Another New Exercise")

        api_client.force_authenticate(user=user)
        url = reverse("api:workout-detail", kwargs={"pk": workout.id})

        new_data = {
            "duration": "01:20:00",
            "volume": new_volume,
            "routine_id": str(workout.routine.id),
            "exercise_logs": [
                {
                    "order": 1,
                    "exercise_id": str(workout.exercise_logs.first().exercise.id),
                    "set_logs": [
                        {
                            "order": 1,
                            "weight": new_weight_1,
                            "reps": new_reps_1,
                        },
                    ],
                },
                {
                    "order": 3,
                    "exercise_id": str(new_exercise.id),
                    "set_logs": [
                        {
                            "order": 1,
                            "weight": new_weight_2,
                            "reps": new_reps_2,
                        },
                        {
                            "order": 2,
                            "weight": new_weight_2 + 5,
                            "reps": new_reps_2 + 2,
                        },
                    ],
                },
            ],
        }

        response = api_client.put(url, new_data, format="json")
        assert response.status_code == STATUS_OK

        workout.refresh_from_db()
        assert str(workout.duration) == "1:20:00"
        assert workout.volume == pytest.approx(new_volume)

        exercise_log_1 = workout.exercise_logs.get(order=1)
        set_log_1 = exercise_log_1.set_logs.first()
        assert set_log_1.weight == pytest.approx(new_weight_1)
        assert set_log_1.reps == new_reps_1

        exercise_log_2 = workout.exercise_logs.get(order=3)
        set_logs_2 = exercise_log_2.set_logs.all()
        assert set_logs_2[0].weight == pytest.approx(new_weight_2)
        assert set_logs_2[0].reps == new_reps_2
        assert set_logs_2[1].weight == pytest.approx(new_weight_2 + 5)
        assert set_logs_2[1].reps == new_reps_2 + 2


class TestRoutineViewSet:
    def test_get_routine_list(
        self,
        user: User,
        api_client: APIClient,
        routine: Routine,
    ):
        api_client.force_authenticate(user=user)
        url = reverse("api:routine-list")

        response = api_client.get(url)
        assert response.status_code == STATUS_OK

        routine_list = response.json()
        assert len(routine_list) > 0
        for routine_data in routine_list:
            assert "id" in routine_data
            assert "name" in routine_data
            assert "routine_exercises" not in routine_data

    def test_get_routine_detail(
        self,
        user: User,
        api_client: APIClient,
        routine: Routine,
    ):
        api_client.force_authenticate(user=user)
        url = reverse("api:routine-detail", kwargs={"pk": routine.id})

        response = api_client.get(url)
        assert response.status_code == STATUS_OK

        routine_data = response.json()
        assert routine_data["name"] == routine.name
        assert len(routine_data["routineExercises"]) == 1

        for routine_exercise in routine_data["routineExercises"]:
            routine_set_count = routine.routine_exercises.last().routine_sets.count()
            assert len(routine_exercise["routineSets"]) == routine_set_count

    def test_create_routine(self, user: User, api_client: APIClient):
        api_client.force_authenticate(user=user)
        url = reverse("api:routine-list")

        new_routine_data = {
            "name": "New Routine",
            "routineExercises": [
                {
                    "order": 1,
                    "exerciseId": str(ExerciseFactory().id),
                    "restTimer": "00:01:00",
                    "note": "Test Note",
                    "routineSets": [
                        {
                            "order": 1,
                            "weight": 10.0,
                            "reps": 11,
                        },
                        {
                            "order": 2,
                            "weight": 20.0,
                            "reps": 12,
                        },
                    ],
                },
            ],
        }

        response = api_client.post(url, new_routine_data, format="json")
        assert response.status_code == STATUS_CREATED

        got_routine_data = response.json()
        assert got_routine_data["name"] == new_routine_data["name"]

        got_routine_exercises = got_routine_data["routineExercises"]
        assert len(got_routine_exercises) == 1
        assert len(got_routine_exercises[0]["routineSets"]) == len(
            new_routine_data["routineExercises"][0]["routineSets"],
        )
        assert (
            got_routine_exercises[0]["routineSets"][0]["order"]
            == new_routine_data["routineExercises"][0]["routineSets"][0]["order"]
        )
        assert (
            got_routine_exercises[0]["routineSets"][1]["order"]
            == new_routine_data["routineExercises"][0]["routineSets"][1]["order"]
        )

    def test_update_routine(self, user: User, api_client: APIClient, routine: Routine):
        api_client.force_authenticate(user=user)
        url = reverse("api:routine-detail", kwargs={"pk": routine.id})

        updated_routine_data = {
            "name": "Updated Routine",
            "routineExercises": [
                {
                    "order": 1,
                    "exerciseId": str(routine.routine_exercises.first().exercise.id),
                    "restTimer": "00:02:00",
                    "note": "Updated Note",
                    "routineSets": [
                        {
                            "order": 1,
                            "weight": 60.0,
                            "reps": 12,
                        },
                    ],
                },
            ],
        }

        response = api_client.put(url, updated_routine_data, format="json")
        assert response.status_code == STATUS_OK

        routine.refresh_from_db()
        assert routine.name == updated_routine_data["name"]
        assert routine.routine_exercises.first().note == "Updated Note"

    def test_delete_routine(self, user: User, api_client: APIClient, routine: Routine):
        api_client.force_authenticate(user=user)
        url = reverse("api:routine-detail", kwargs={"pk": routine.id})

        response = api_client.delete(url)
        assert response.status_code == STATUS_NO_CONTENT

        with pytest.raises(Routine.DoesNotExist):
            routine.refresh_from_db()


class TestExerciseViewSet:
    def test_get_exercise_list(
        self,
        user: User,
        api_client: APIClient,
        exercise: Exercise,
    ):
        api_client.force_authenticate(user=user)
        url = reverse("api:exercise-list")

        response = api_client.get(url)
        assert response.status_code == STATUS_OK

        exercise_list = response.json()
        assert len(exercise_list) > 0
        for exercise_data in exercise_list:
            assert "name" in exercise_data
            assert "primaryMuscleGroup" in exercise_data
            assert "exerciseType" not in exercise_data
            assert "equipment" not in exercise_data

    def test_get_exercise_detail(
        self,
        user: User,
        api_client: APIClient,
        exercise: Exercise,
    ):
        api_client.force_authenticate(user=user)
        url = reverse("api:exercise-detail", kwargs={"pk": exercise.id})

        response = api_client.get(url)
        assert response.status_code == STATUS_OK

        exercise_data = response.json()
        assert exercise_data["name"] == exercise.name
        assert exercise_data["exerciseType"] == exercise.exercise_type
        assert exercise_data["equipment"] == exercise.equipment
        assert exercise_data["primaryMuscleGroup"] == exercise.primary_muscle_group
        assert exercise_data["smallImage"] is not None
        assert exercise_data["largeImage"] is not None

    def test_create_exercise(self, user: User, api_client: APIClient):
        api_client.force_authenticate(user=user)
        url = reverse("api:exercise-list")
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04"
            b"\x04\x00\x00\x00\x2c\x00\x00\x00"
            b"\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
        )
        small_image = SimpleUploadedFile(
            name="small_image.jpg",
            content=small_gif,
            content_type="image/jpeg",
        )
        large_image = SimpleUploadedFile(
            name="large_image.jpg",
            content=small_gif,
            content_type="image/jpeg",
        )
        payload = {
            "name": "New Exercise",
            "exerciseType": Exercise.ExerciseTypes.WEIGHT_REPS.value,
            "equipment": Exercise.Equipments.BARBELL.value,
            "primaryMuscleGroup": Exercise.MuscleGroups.BICEPS.value,
            "otherMuscles": [
                Exercise.MuscleGroups.FOREARMS.value,
                Exercise.MuscleGroups.SHOULDERS.value,
            ],
            "smallImage": small_image,
            "largeImage": large_image,
        }

        response = api_client.post(url, payload, format="multipart")
        assert response.status_code == STATUS_CREATED

        got_exercise = response.json()
        assert got_exercise["name"] == payload["name"]
        assert got_exercise["exerciseType"] == payload["exerciseType"]
        assert got_exercise["equipment"] == payload["equipment"]
        assert got_exercise["primaryMuscleGroup"] == payload["primaryMuscleGroup"]
        assert set(got_exercise["otherMuscles"]) == set(payload["otherMuscles"])
        assert got_exercise["smallImage"] is not None
        assert got_exercise["largeImage"] is not None

    def test_update_exercise(
        self,
        user: User,
        api_client: APIClient,
        exercise: Exercise,
    ):
        api_client.force_authenticate(user=user)
        url = reverse("api:exercise-detail", kwargs={"pk": exercise.id})

        payload = {
            "name": "Updated Exercise",
            "exerciseType": exercise.exercise_type,
            "equipment": exercise.equipment,
            "primaryMuscleGroup": exercise.primary_muscle_group,
            "otherMuscles": exercise.other_muscles.split(","),
        }

        response = api_client.put(url, payload, format="json")
        assert response.status_code == STATUS_OK

        exercise.refresh_from_db()
        assert exercise.name == payload["name"]

    def test_delete_exercise(
        self,
        user: User,
        api_client: APIClient,
        exercise: Exercise,
    ):
        api_client.force_authenticate(user=user)
        url = reverse("api:exercise-detail", kwargs={"pk": exercise.id})

        response = api_client.delete(url)
        assert response.status_code == STATUS_NO_CONTENT

        with pytest.raises(Exercise.DoesNotExist):
            exercise.refresh_from_db()
