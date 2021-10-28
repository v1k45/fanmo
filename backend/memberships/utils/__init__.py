import razorpay
from django.conf import settings

razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET)
)
razorpay_client.set_app_details({"title": "Memberships", "version": "0.1"})
