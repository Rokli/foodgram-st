from rest_framework.decorators import action
from rest_framework import viewsets, pagination, mixins, permissions
from .models import User, Follow
from .serializers import UsertSerializer, FollowSerializer
from rest_framework.response import Response
from rest_framework import viewsets, pagination, mixins, permissions, status

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
    @action(detail=False, methods=['get'], url_path='profile')
    def fetch_current(self, request):
        return Response(self.get_serializer(request.user).data)

    @action(detail=False, methods=['put', 'delete'], url_path='profile/avatar')
    def update_remove_avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            if user.avatar:
                user.avatar.delete()

            serializer.save()
            return Response({'avatar': serializer.data['avatar']}, status=status.HTTP_200_OK)

        user.avatar.delete()
        user.save()
        return Response({'message': 'Avatar successfully removed'}, status=status.HTTP_204_NO_CONTENT)
