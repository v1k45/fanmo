import re
import bisect

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.core import validators
from memberships.users.wordlist import reserved_usernames


@deconstructible
class ASCIIUsernameValidator(validators.RegexValidator):
    regex = r"^[\w-]+\Z"
    message = "Enter a valid username. This value may contain only letters, numbers, dashes and underscores."
    flags = re.ASCII


def validate_username(username):
    username = username.lower()
    idx = bisect.bisect_left(reserved_usernames, username)
    if reserved_usernames[idx] == username:
        raise ValidationError("This username is already taken.", "already_taken")
    return username
