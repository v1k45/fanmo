from typing import Any

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest
from django.utils import timezone


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def send_confirmation_mail(self, request, email_device, signup):
        # do not send confirmation email immediately on signup
        if signup:
            return

        # regenerate otp if the current one is expired.
        if email_device.valid_until < timezone.now():
            email_device.generate_token()

        self.send_mail(
            "account/email/email_confirmation",
            email_device.user.email,
            {
                "request": request,
                "user": email_device.user,
                "otp": email_device.token,
                "current_site": get_current_site(request),
            },
        )

    def confirm_email(self, request, email_address):
        super().confirm_email(request, email_address)
        email_address.user.email_verified = True
        email_address.user.save()

    def send_password_reset_mail(self, request, email_device):
        if email_device.valid_until < timezone.now():
            email_device.generate_token()

        self.send_mail(
            "account/email/password_reset_key",
            email_device.user.email,
            {
                "request": request,
                "user": email_device.user,
                "otp": email_device.token,
                "current_site": get_current_site(request),
            },
        )


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest, sociallogin: Any):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)
