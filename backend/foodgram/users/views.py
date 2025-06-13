from rest_framework import status, permissions, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.views import UserViewSet
from .models import User
from .serializers import UsersSerializer

class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'], url_path='profile', permission_classes=[permissions.IsAuthenticated])
    def retrieve_profile(self, request):
        data = self.get_serializer(request.user).data
        return Response(data)

    @action(detail=True, methods=['get'], url_path='', permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def fetch_user(self, request, pk=None):
        user = self.get_object()
        data = self.get_serializer(user).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put', 'delete'], url_path='profile/avatar', permission_classes=[permissions.IsAuthenticated])
    def update_remove_avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            avatar = request.data.get('avatar')
            if not avatar:
                return Response({'avatar': 'Avatar field is required!'}, status=status.HTTP_400_BAD_REQUEST)
            if user.avatar:
                user.avatar.delete()
            serializer.save()
            return Response({'avatar': serializer.data['avatar']}, status=status.HTTP_200_OK)
        if not user.avatar:
            return Response({'detail': 'No avatar exists'}, status=status.HTTP_400_BAD_REQUEST)
        user.avatar.delete()
        user.save()
        return Response({'message': 'Avatar removed'}, status=status.HTTP_204_NO_CONTENT)