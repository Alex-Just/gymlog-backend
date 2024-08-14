from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from gymlog.gym.api.serializers import ExerciseDetailSerializer
from gymlog.gym.api.serializers import ExerciseListSerializer
from gymlog.gym.api.serializers import RoutineDetailSerializer
from gymlog.gym.api.serializers import RoutineListSerializer
from gymlog.gym.api.serializers import SetLogSerializer
from gymlog.gym.api.serializers import WorkoutSerializer
from gymlog.gym.models import Exercise
from gymlog.gym.models import Routine
from gymlog.gym.models import SetLog
from gymlog.gym.models import Workout


class ExerciseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Exercise.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return ExerciseListSerializer
        return ExerciseDetailSerializer


class WorkoutViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WorkoutSerializer

    def get_queryset(self):
        return Workout.objects.filter(routine__user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class SetLogViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SetLogSerializer

    def get_queryset(self):
        return SetLog.objects.filter(
            exercise_log__workout__routine__user=self.request.user,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class RoutineViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Routine.objects.all()

    def get_queryset(self):
        qs = Routine.objects.filter(user=self.request.user)
        if self.action == "list":
            qs = qs.prefetch_related(
                "routine_exercises__exercise",
                "routine_exercises__routine_sets",
            )
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return RoutineListSerializer
        return RoutineDetailSerializer
