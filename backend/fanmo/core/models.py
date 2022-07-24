from django.db import models


class NotificationType(models.TextChoices):
    # creator memberships
    NEW_MEMBER = "new_member"
    MEMBER_CHANGE = "member_change"
    MEMBER_RENEW = "member_renew"
    MEMBER_CANCELLATION_SCHEDULED = "member_cancellation_scheduled"
    MEMBER_PAYMENT_FAILED = "member_payment_failed"
    MEMBER_HALTED = "member_halted"
    # fan memberships
    NEW_MEMBERSHIP = "new_membership"
    MEMBERSHIP_RENEW = "membership_renew"
    MEMBERSHIP_CHANGE = "membership_change"
    MEMBERSHIP_CANCELLATION_SCHEDULED = "membership_cancellation_scheduled"
    MEMBERSHIP_PAYMENT_FAILED = "membership_payment_failed"
    MEMBERSHIP_HALTED = "membership_halted"

    DONATION_RECEIVED = "donation_received"
    DONATION_SENT = "donation_sent"

    NEW_POST = "new_post"
    COMMENT = "comment"
    COMMENT_REPLY = "comment_reply"

    MARKETING = "marketing"
    PASSWORD_CHANGE = "password_change"
    CREATOR_APPROVED = "creator_approved"


POST_NOTIFICATIONS = [NotificationType.NEW_POST]
COMMENT_NOTIFICATIONS = [NotificationType.COMMENT]
COMMENT_REPLY_NOTIFICATIONS = [NotificationType.COMMENT_REPLY]
DONATION_NOTIFICATIONS = [
    NotificationType.DONATION_RECEIVED,
    NotificationType.DONATION_SENT,
]
MEMBERSHIP_NOTIFICATIONS = [
    NotificationType.NEW_MEMBER,
    NotificationType.MEMBER_CHANGE,
    NotificationType.MEMBER_RENEW,
    NotificationType.MEMBER_CANCELLATION_SCHEDULED,
    NotificationType.MEMBER_PAYMENT_FAILED,
    NotificationType.MEMBER_HALTED,
    NotificationType.NEW_MEMBERSHIP,
    NotificationType.MEMBERSHIP_RENEW,
    NotificationType.MEMBERSHIP_CHANGE,
    NotificationType.MEMBERSHIP_CANCELLATION_SCHEDULED,
    NotificationType.MEMBERSHIP_PAYMENT_FAILED,
    NotificationType.MEMBERSHIP_HALTED,
]
MARKETING_NOTIFICATIONS = [NotificationType.MARKETING]
