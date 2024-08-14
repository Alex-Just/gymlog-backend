from uuid import UUID

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from gymlog.users.models import User

from .serializers import UserSerializer


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, (str, UUID))
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False, methods=["get", "put"])
    def me(self, request):
        if request.method == "PUT":
            s = self.get_serializer(request.user, data=request.data, partial=True)
            s.is_valid(raise_exception=True)
            s.save()
            return Response(s.data, status=status.HTTP_200_OK)

        s = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=s.data)
