import uuid
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied
from activitylog.utils import record_activity
from .models import Post, Comment, Like, Save, Share
from .serializers import PostSerializer, CommentSerializer, CreateCommentSerializer, CreatePostSerializer


class PostListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.filter(deleted_at__isnull=True).prefetch_related('comments', 'likes', 'shares', 'saves')
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        # Only admins can create posts
        if request.user.role != 'ADMIN':
            raise PermissionDenied('Only admins can create posts')

        serializer = CreatePostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post = Post.objects.create(
            id=str(uuid.uuid4()),
            author=request.user,
            content=serializer.validated_data['content'],
            image=serializer.validated_data.get('image', '')
        )

        record_activity(
            action='CREATE',
            entity_type='Post',
            entity_id=str(post.id),
            actor=request.user,
            details={'content_length': len(post.content)}
        )

        return Response(PostSerializer(post, context={'request': request}).data, status=201)


class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Post.objects.get(id=pk, deleted_at__isnull=True)
        except Post.DoesNotExist:
            raise NotFound('Post not found')

    def delete(self, request, pk):
        post = self.get_object(pk)

        if request.user != post.author and request.user.role != 'ADMIN':
            raise PermissionDenied('You can only delete your own posts')

        post.deleted_at = timezone.now()
        post.save(update_fields=['deleted_at'])

        record_activity(
            action='DELETE',
            entity_type='Post',
            entity_id=str(post.id),
            actor=request.user
        )

        return Response({'id': pk})


class CommentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id, deleted_at__isnull=True)
        except Post.DoesNotExist:
            raise NotFound('Post not found')

        serializer = CreateCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = Comment.objects.create(
            id=str(uuid.uuid4()),
            post=post,
            author=request.user,
            content=serializer.validated_data['content']
        )

        record_activity(
            action='CREATE',
            entity_type='Comment',
            entity_id=str(comment.id),
            actor=request.user,
            details={'post_id': post_id}
        )

        return Response(CommentSerializer(comment).data, status=201)


class CommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id, deleted_at__isnull=True)
        except Comment.DoesNotExist:
            raise NotFound('Comment not found')

        if request.user != comment.author and request.user.role != 'ADMIN':
            raise PermissionDenied('You can only delete your own comments')

        comment.deleted_at = timezone.now()
        comment.save(update_fields=['deleted_at'])

        record_activity(
            action='DELETE',
            entity_type='Comment',
            entity_id=str(comment.id),
            actor=request.user
        )

        return Response({'id': comment_id})


class LikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id, deleted_at__isnull=True)
        except Post.DoesNotExist:
            raise NotFound('Post not found')

        like, created = Like.objects.get_or_create(post=post, user=request.user, defaults={'id': str(uuid.uuid4())})

        if not created:
            like.delete()
            return Response({'liked': False})

        record_activity(
            action='CREATE',
            entity_type='Like',
            entity_id=str(like.id),
            actor=request.user,
            details={'post_id': post_id}
        )

        return Response({'liked': True})


class SaveToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id, deleted_at__isnull=True)
        except Post.DoesNotExist:
            raise NotFound('Post not found')

        save, created = Save.objects.get_or_create(post=post, user=request.user, defaults={'id': str(uuid.uuid4())})

        if not created:
            save.delete()
            return Response({'saved': False})

        record_activity(
            action='CREATE',
            entity_type='Save',
            entity_id=str(save.id),
            actor=request.user,
            details={'post_id': post_id}
        )

        return Response({'saved': True})


class ShareToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id, deleted_at__isnull=True)
        except Post.DoesNotExist:
            raise NotFound('Post not found')

        share, created = Share.objects.get_or_create(post=post, user=request.user, defaults={'id': str(uuid.uuid4())})

        if not created:
            share.delete()
            return Response({'shared': False})

        record_activity(
            action='CREATE',
            entity_type='Share',
            entity_id=str(share.id),
            actor=request.user,
            details={'post_id': post_id}
        )

        return Response({'shared': True})
