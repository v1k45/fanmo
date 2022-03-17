from decimal import Decimal

from moneyed import Money, get_currency


def money_from_sub_unit(amount, currency_code):
    currency = get_currency(currency_code)
    return Money(Decimal(amount) / currency.sub_unit, currency.code)


def deduct_platform_fee(money, creator_user):
    return money * (
        1 - Decimal(creator_user.user_preferences.platform_fee_percent / 100)
    )
