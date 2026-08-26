from django.urls import path
from .views import (
    PostListCreateView,
    PostDetailView,
    CommentListCreateView,
    CommentDeleteView,
    LikeToggleView,
    SaveToggleView,
    ShareToggleView,
)

urlpatterns = [
    path('', PostListCreateView.as_view()),
    path('/<uuid:pk>', PostDetailView.as_view()),
    path('/<uuid:post_id>/comments', CommentListCreateView.as_view()),
    path('/comments/<uuid:comment_id>', CommentDeleteView.as_view()),
    path('/<uuid:post_id>/like', LikeToggleView.as_view()),
    path('/<uuid:post_id>/save', SaveToggleView.as_view()),
    path('/<uuid:post_id>/share', ShareToggleView.as_view()),
]
