from rest_framework.decorators import action
from rest_framework import viewsets, pagination, mixins, permissions
from .models import Account, Follow
from .serializers import AccountSerializer, FollowSerializer


class SubscriptionViewSet(viewsets.GenericViewSet,
                         mixins.CreateModelMixin,
                         mixins.DestroyModelMixin):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    pagination_class = pagination.LimitOffsetPagination