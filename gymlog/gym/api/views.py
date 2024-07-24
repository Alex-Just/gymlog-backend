from rest_framework import viewsets
from rest_framework.response import Response

from gymlog.gym.api.serializers import SetLogSerializer
from gymlog.gym.api.serializers import WorkoutSerializer
from gymlog.gym.models import SetLog
from gymlog.gym.models import Workout


class WorkoutViewSet(viewsets.ModelViewSet):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer

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
    queryset = SetLog.objects.all()
    serializer_class = SetLogSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)