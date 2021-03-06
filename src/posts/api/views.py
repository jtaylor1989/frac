from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from posts.models import Post
from .permissions import IsOwnerOrReadOnly, IsOwnerOrAdmin

from . import serializers


class PostCreateAPIView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostCreateSerializer

    def perform_create(self, serializer):
        '''
        Ensures the logged in user created this post
        '''
        return serializer.save(user=self.request.user)


class PostDetailAPIView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostDetailSerializer
    lookup_field = 'slug'


class PostUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostCreateSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    lookup_field = 'slug'

    def perform_update(self, serializer):
        """
        Sets the user to the logged in user.
        """
        serializer.save(user=self.request.user)


class PostDeleteAPIView(generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostDetailSerializer
    permission_classes = (IsOwnerOrAdmin,)
    lookup_field = 'slug'

    def get(self, request, slug, format=None):
        context = {'message':
                        'Proceed with the Deletion by clicking the Delete button.'}
        return Response(context)


class PostListAPIView(generics.ListAPIView):
    serializer_class = serializers.PostListSerializer

    def get_queryset(self, *args, **kwargs):
        '''
        Only diplsay my posts and the users I follow
        '''
        im_following = self.request.user.profile.get_following()
        qs_others = Post.objects.filter(user__in=im_following)
        qs_me = Post.objects.filter(user=self.request.user)
        qs_total = (qs_others | qs_me).distinct()
        return qs_total


class LikeToggleAPIView(APIView):
    '''
    Uses the custom model manager for Like toggle button.
    Users can't like their own posts.
    '''
    def get(self, request, slug, format=None):
        post_qs = Post.objects.filter(slug=slug)
        message = 'Not allowed'
        if request.user.is_authenticated() and not request.user.id == post_qs.first().user.id:
            liked_post = Post.objects.toggle_like(request.user, post_qs.first())
            return Response({'liked': liked_post})
        return Response({'message': message}, status=400)
