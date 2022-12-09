from decimal import Decimal

from moneyed import INR

from fanmo.utils.money import Money

DONATION_TIERS = [
    {
        "name": "level_1",
        "min_amount": Money(Decimal("50"), INR),
        "max_length": 50,
    },
    {
        "name": "level_2",
        "min_amount": Money(Decimal("100"), INR),
        "max_length": 150,
    },
    {
        "name": "level_3",
        "min_amount": Money(Decimal("250"), INR),
        "max_length": 200,
    },
    {
        "name": "level_4",
        "min_amount": Money(Decimal("500"), INR),
        "max_length": 250,
    },
    {
        "name": "level_5",
        "min_amount": Money(Decimal("1000"), INR),
        "max_length": 300,
    },
    {
        "name": "level_6",
        "min_amount": Money(Decimal("2500"), INR),
        "max_length": 350,
    },
    {
        "name": "level_7",
        "min_amount": Money(Decimal("5000"), INR),
        "max_length": 500,
    },
]
