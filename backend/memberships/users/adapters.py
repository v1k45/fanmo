from collections import namedtuple
from typing import Any

from django_otp.plugins.otp_email.models import EmailDevice
from allauth.account.utils import setup_user_email, user_username
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest
from django.utils import timezone

import random
from .wordlist import adjectives, animals


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_username(self, request, user):
        username = user.username or self.generate_unique_username(
            [user.name, user.email, user.username, "user"]
        )
        user_username(user, username)

    def save_user(self, request, user, form, commit=True):
        user.name = form.cleaned_data.get("name")
        if not user.name:
            user.name = self.generate_name()
        user.is_creator = form.cleaned_data.get("is_creator", None)
        return super().save_user(request, user, form, commit)

    def generate_name(self):
        adjective = random.choice(adjectives)
        animal = random.choice(animals)
        return f"{adjective} {animal}".title()

    def format_email_subject(self, subject):
        return subject

    def send_confirmation_mail(self, request, email_device, signup):
        # do not send confirmation email immediately on signup
        if signup:
            return

        # regenerate otp if the current one is expired.
        if email_device.valid_until < timezone.now():
            email_device.generate_token()

        self.send_mail(
            "maizzle/email_verification",
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

    def send_password_reset_mail(self, request, email_device, invite_intent=None):
        if email_device.valid_until < timezone.now():
            email_device.generate_token()

        template = "password_reset" if invite_intent is None else "account_activate"
        self.send_mail(
            f"maizzle/{template}",
            email_device.user.email,
            {
                "request": request,
                "user": email_device.user,
                "otp": email_device.token,
                "current_site": get_current_site(request),
            },
        )

    def invite(self, request, email):
        form = namedtuple("Form", ["cleaned_data"])(
            cleaned_data={"email": email, "is_creator": False}
        )
        user = self.new_user(request)
        user = self.save_user(request, user, form)
        setup_user_email(request, user, [])

        # send welcome email with OTP
        email_device, _ = EmailDevice.objects.get_or_create(user=user)
        self.send_password_reset_mail(request, email_device, invite_intent=True)
        return user


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        user.name = f"{user.first_name} {user.last_name}".strip()
        user.email_verified = True
        return user

    def is_open_for_signup(self, request: HttpRequest, sociallogin: Any):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)
