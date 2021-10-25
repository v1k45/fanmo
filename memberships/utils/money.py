from moneyed import get_currency, Money
from decimal import Decimal


def money_from_sub_unit(amount, currency_code):
    currency = get_currency(currency_code)
    return Money(Decimal(amount) / currency.sub_unit, currency.code)


def deduct_platform_fee(money, seller):
    return money * (1 - Decimal(seller.user_preferences.platform_fee_percent / 100))
