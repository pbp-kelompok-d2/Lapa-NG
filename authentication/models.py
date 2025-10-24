from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import re

digit_validator = RegexValidator(
    regex=r'^\d+$',
    message='Phone number must contain only digits.'
)

class CustomUser(models.Model):
    ROLES = [
        ('owner', 'Owner'),
        ('customer', 'Customer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLES, default='owner')
    number = models.CharField(max_length=11, validators=[digit_validator])
    profile_picture = models.URLField(blank=True,null=True)

    @property
    def formatted_number(self):
        return format_indonesia_number(self.number)

def normalize_indonesia_number(raw):
    """
    Remove non-digits and strip leading +62, 62, or leading 0 so we return the local
    national significant number (no leading zero).
    Example:
      '+6285890239087' -> '85890239087'
      '085890239087'   -> '85890239087'
      '6285890239087'  -> '85890239087'
    """
    if not raw:
        return ''
    digits = re.sub(r'\D', '', str(raw))
    # strip leading country code or leading zero
    if digits.startswith('62'): 
        digits = digits[2:]
    elif digits.startswith('0'):
        digits = digits[1:]
    return digits


def format_indonesia_number(raw):
    """
    Format normalized Indonesian:
      '+62 ' + groups joined with '-'
    Grouping rules=:
      - length == 11 -> 3-4-4 (e.g. '85890239087' -> '858-9023-9087')
      - length == 10 -> 3-3-4 (e.g. '8029039775' -> '802-903-9775')
      - else -> try sensible grouping: first 3, middle (len-7), last 4
    """
    digits = normalize_indonesia_number(raw)
    if not digits:
        return ''

    n = len(digits)

    if n == 11:
        parts = [digits[:3], digits[3:7], digits[7:]]
    elif n == 10:
        parts = [digits[:3], digits[3:6], digits[6:]]
    elif n > 7:
        # first 3, middle (n-7), last 4
        mid_len = n - 7
        parts = [digits[:3], digits[3:3 + mid_len], digits[-4:]]
    elif n > 4:
        # fall back to splitting into (prefix, suffix)
        parts = [digits[:-4], digits[-4:]]
    else:
        parts = [digits]

    return f"+62 {'-'.join(p for p in parts if p)}"

