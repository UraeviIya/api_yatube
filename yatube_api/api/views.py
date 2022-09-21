from api.serializers import CommentSerializer, GroupSerializer, PostSerializer
from django.shortcuts import get_object_or_404
from posts.models import Comment, Group, Post
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from .permissions import IsAuthorOrReadOnly

# 403 Forbidden Неверны авторизационные данные, указанные в запросе
# или запрещен доступ к запрашиваемому ресурсу.
API_RAISE_403 = PermissionDenied('Изменение чужого контента запрещено!')


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise API_RAISE_403
        super(PostViewSet, self).perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise API_RAISE_403
        instance.delete()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return Comment.objects.filter(post=post)

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user, post=post)
