from decimal import Decimal

from djmoney.money import Money
from moneyed import get_currency


def money_from_sub_unit(amount, currency_code):
    currency = get_currency(currency_code)
    return Money(Decimal(amount) / currency.sub_unit, currency.code)


def money_to_sub_unit(money):
    """
    Convert money value to sub units (Ruppee to Paisa)
    A 2 decimal place rounding is added to maintain consistency with other parts of the codebase.

    e.g., 5.706 is interpreted as 5.71 by the system. To ensure the rounding is not lost, we round it before converting.
    """
    return money.round(2).get_amount_in_sub_unit()


def deduct_platform_fee(money, creator_user):
    return money * (
        1 - Decimal(creator_user.user_preferences.platform_fee_percent / 100)
    )


def percent_change(current, previous):
    if current == previous:
        return Decimal(0)
    try:
        return ((current - previous) / previous) * Decimal("100.0")
    except ZeroDivisionError:
        return Decimal("100.0")
