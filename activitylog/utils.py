from .models import ActivityLog


# Every module that changes something calls this instead of writing to
# activity_log directly, so logging happens consistently and no action
# slips through unrecorded.
def record_activity(*, action, entity_type, entity_id=None, actor=None, details=None):
    return ActivityLog.objects.create(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        actor=actor,
        details=details,
    )
