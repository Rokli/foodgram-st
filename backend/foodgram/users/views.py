from djoser.views import UserViewSet
from rest_framework import status, permissions, pagination
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import User
from .serializers import UsersSerializer


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(
        detail=False, 
        methods=['get'], 
        url_path='me', 
        permission_classes=[permissions.IsAuthenticated]
    )
    def get_current_user(self, request):
        user_data = self.get_serializer(request.user).data
        return Response(user_data)

    @action(
        detail=True, 
        methods=['get'], 
        url_path='', 
        permission_classes=[permissions.IsAuthenticatedOrReadOnly]
    )
    def get_user_profile(self, request, pk=None):
        target_user = self.get_object()
        user_data = self.get_serializer(target_user).data
        return Response(user_data, status=status.HTTP_200_OK)

    @action(
        detail=False, 
        methods=['put', 'delete'], 
        url_path='me/avatar',
        permission_classes=[permissions.IsAuthenticated]
    )
    def manage_user_avatar(self, request):
        current_user = request.user
        
        if request.method == 'PUT':
            serializer = self.get_serializer(
                current_user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            
            avatar_data = request.data.get('avatar')
            if not avatar_data:
                return Response(
                    {'avatar': 'Поле аватара обязательно!'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if current_user.profile_picture:
                current_user.profile_picture.delete()
                
            serializer.save()
            return Response(
                {'avatar': serializer.data['avatar']}, 
                status=status.HTTP_200_OK
            )
            
        if not current_user.profile_picture:
            return Response(
                {'detail': 'Аватар не установлен'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        current_user.profile_picture.delete()
        current_user.save()
        return Response(
            {'message': 'Аватар удален'}, 
            status=status.HTTP_204_NO_CONTENT
        )