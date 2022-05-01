import json
from django_q.tasks import async_task

from django.conf import settings
from django.db.transaction import non_atomic_requests
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from razorpay.errors import SignatureVerificationError

from memberships.utils import razorpay_client
from memberships.webhooks.models import WebhookMessage
from memberships.webhooks.tasks import process_razorpay_webhook


@csrf_exempt
@require_POST
@non_atomic_requests
def razorpay_webhook(request):
    request_body = request.body.decode("utf-8")
    try:
        razorpay_client.utility.verify_webhook_signature(
            request_body,
            request.headers["X-Razorpay-Signature"],
            settings.RAZORPAY_WEBHOOK_SECRET,
        )
    except (SignatureVerificationError, KeyError):
        return HttpResponseForbidden("Invalid payload.", content_type="text/plain")

    event_id = request.headers["x-razorpay-event-id"]
    if WebhookMessage.objects.filter(external_id=event_id).exists():
        return HttpResponse("Already Received.", content_type="text/plain")

    payload = json.loads(request_body)
    webhook_message = WebhookMessage.objects.create(
        sender=WebhookMessage.Sender.RAZORPAY,
        external_id=event_id,
        payload=payload,
    )
    async_task(process_razorpay_webhook, webhook_message.pk)
    return HttpResponse("Ok.", content_type="text/plain")
