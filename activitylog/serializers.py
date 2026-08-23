from rest_framework import serializers
from .models import ActivityLog


class ActorSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    email = serializers.EmailField()


class ActivityLogSerializer(serializers.ModelSerializer):
    actor = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = ['id', 'action', 'entity_type', 'entity_id', 'details', 'actor', 'created_at']

    def get_actor(self, obj):
        if not obj.actor:
            return None
        return {'id': obj.actor.id, 'name': obj.actor.name, 'email': obj.actor.email}
