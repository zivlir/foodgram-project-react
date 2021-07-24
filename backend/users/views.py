from djoser import views

from users.models import User
from users.serializers import AuthorSerializer
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import Follow
from api.serializers import FollowSerializer
class AuthorViewSet(views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]

    @action(methods=['GET', 'DELETE'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, author_id=None):
        user = self.request.user
        following = get_object_or_404(User, id=author_id)
        if request.method == 'GET':
            new_follow = Follow.objects.create(user=user, author=following)
            new_follow.save()
            serializer = FollowSerializer(instance=following, context={'request': request})
            return Response(serializer.data)

    @action(detail=False)
    def subscriptions(self, request):
        print('subscriptions_list')
        user = self.request.user
        follow = Follow.objects.filter(user=user)
        serializer = FollowSerializer(instance=follow, context={'request': request})