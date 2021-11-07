import json
from secrets import compare_digest

from django.conf import settings
from django.db.transaction import non_atomic_requests
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from memberships.utils import razorpay_client
from memberships.webhooks.models import WebhookMessage
from razorpay.errors import SignatureVerificationError

from memberships.webhooks.tasks import process_razorpay_webhook


@csrf_exempt
@require_POST
@non_atomic_requests
def razorpay_webhook(request):
    try:
        razorpay_client.utility.verify_webhook_signature(
            request.body,
            request.headers["X-Razorpay-Signature"],
            settings.RAZORPAY_WEBHOOK_SECRET,
        )
    except (SignatureVerificationError, KeyError):
        return HttpResponseForbidden("Invalid payload.", content_type="text/plain")

    event_id = request.headers["x-razorpay-event-id"]
    if WebhookMessage.objects.filter(external_id=event_id).exists():
        return HttpResponse("Already Received.", content_type="text/plain")

    payload = json.loads(request.body)
    webhook_message = WebhookMessage.objects.create(
        sender=WebhookMessage.Sender.RAZORPAY,
        external_id=event_id,
        payload=payload,
    )
    process_razorpay_webhook(webhook_message.pk)
    return HttpResponse("Ok.", content_type="text/plain")