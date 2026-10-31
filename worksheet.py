"""Question generation for the Daily Practice worksheet."""

from __future__ import annotations

import random
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction


@dataclass(frozen=True)
class Question:
    prompt: str
    answer: str
    category: str


SINGLE_CATEGORIES = {
    "整数加法": "integer_add",
    "整数减法": "integer_subtract",
    "整数加减法": "integer_add_subtract",
    "整数乘法": "integer_multiply",
    "整数除法": "integer_divide",
    "整数乘除法": "integer_multiply_divide",
    "分数加法": "fraction_add",
    "分数减法": "fraction_subtract",
    "分数乘法": "fraction_multiply",
    "分数除法": "fraction_divide",
    "两分数四则运算": "fraction_two_four_operations",
    "三分数乘除法": "fraction_three_multiply_divide",
    "单位换算": "unit_conversion",
    "百分数加法": "percent_add",
    "百分数减法": "percent_subtract",
    "百分数乘法": "percent_multiply",
    "百分数除法": "percent_divide",
    "小数加法": "decimal_add",
    "小数减法": "decimal_subtract",
    "小数乘法": "decimal_multiply",
    "小数除法": "decimal_divide",
}

MIXED_CATEGORIES = tuple(dict.fromkeys(SINGLE_CATEGORIES.values()))
MIXED_CATEGORIES = tuple(
    category for category in MIXED_CATEGORIES
    if category not in {"integer_add_subtract", "integer_multiply_divide"}
)


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _decimal_text(value: Fraction, max_places: int = 12) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    denominator = value.denominator
    twos = fives = 0
    while denominator % 2 == 0:
        twos += 1
        denominator //= 2
    while denominator % 5 == 0:
        fives += 1
        denominator //= 5
    if denominator == 1:
        places = max(twos, fives)
        if places <= max_places:
            result = Decimal(value.numerator) / Decimal(value.denominator)
            return format(result, f".{places}f").rstrip("0").rstrip(".") or "0"
    return _fraction_text(value)


def _random_fraction() -> Fraction:
    denominator = random.randint(2, 12)
    numerator = random.randint(1, denominator - 1)
    return Fraction(numerator, denominator)


def _random_decimal() -> Decimal:
    places = random.randint(1, 3)
    scale = 10**places
    return Decimal(random.randint(1, 9999)) / Decimal(scale)


def _integer_division() -> tuple[int, int, int]:
    valid = [(n, d, n // d) for n in range(1, 100) for d in range(2, 13) if n % d == 0]
    return random.choice(valid)


def _unit_conversion_question() -> Question:
    """Generate an exact conversion between adjacent metric/time units."""
    pairs = (
        ("km", "m", 1_000, "length"),
        ("m", "cm", 100, "length"),
        ("cm", "mm", 10, "length"),
        ("L", "ml", 1_000, "volume"),
        ("hours", "minutes", 60, "time"),
        ("minutes", "seconds", 60, "time"),
        ("km²", "m²", 1_000_000, "area"),
        ("m²", "cm²", 10_000, "area"),
        ("cm²", "mm²", 100, "area"),
    )
    larger, smaller, factor, family = random.choice(pairs)
    if random.choice((True, False)):
        amount = random.randint(2, 20 if family == "area" else 99)
        source, target, answer = larger, smaller, amount * factor
    else:
        answer = random.randint(2, 20 if family == "area" else 99)
        source, target, amount = smaller, larger, answer * factor
    return Question(f"Convert: {amount} {source} = ______ {target}", str(answer), "unit_conversion")


def generate_question(category: str) -> Question:
    """Generate one exact, one-step arithmetic question."""
    if category == "unit_conversion":
        return _unit_conversion_question()

    if category == "integer_add_subtract":
        return generate_question(random.choice(("integer_add", "integer_subtract")))
    if category == "integer_multiply_divide":
        return generate_question(random.choice(("integer_multiply", "integer_divide")))

    if category in {"integer_add", "integer_subtract"}:
        a, b = random.randint(10, 999), random.randint(10, 999)
        if category == "integer_add":
            return Question(f"{a} + {b} =", str(a + b), category)
        a, b = max(a, b), min(a, b)
        return Question(f"{a} - {b} =", str(a - b), category)

    if category == "integer_multiply":
        a, b = random.randint(10, 99), random.randint(10, 99)
        return Question(f"{a} x {b} =", str(a * b), category)

    if category == "integer_divide":
        a, b, answer = _integer_division()
        return Question(f"{a} ÷ {b} =", str(answer), category)

    if category.startswith("fraction_"):
        if category == "fraction_two_four_operations":
            a, b = _random_fraction(), _random_fraction()
            op = random.choice(("add", "subtract", "multiply", "divide"))
        elif category == "fraction_three_multiply_divide":
            a, b, c = _random_fraction(), _random_fraction(), _random_fraction()
            first_op, second_op = random.choice(("multiply", "divide")), random.choice(("multiply", "divide"))
            first_symbol = {"multiply": "x", "divide": "÷"}[first_op]
            second_symbol = {"multiply": "x", "divide": "÷"}[second_op]
            answer = a * b if first_op == "multiply" else a / b
            answer = answer * c if second_op == "multiply" else answer / c
            return Question(
                f"{_fraction_text(a)} {first_symbol} {_fraction_text(b)} {second_symbol} {_fraction_text(c)} =",
                _fraction_text(answer), category,
            )
        else:
            a, b = _random_fraction(), _random_fraction()
            op = category.split("_")[1]
        if op == "add":
            answer = a + b
        elif op == "subtract":
            a, b = max(a, b), min(a, b)
            answer = a - b
        elif op == "multiply":
            answer = a * b
        else:
            answer = a / b
        symbol = {"add": "+", "subtract": "-", "multiply": "x", "divide": "÷"}[op]
        return Question(f"{_fraction_text(a)} {symbol} {_fraction_text(b)} =", _fraction_text(answer), category)

    if category.startswith("percent_"):
        op = category.split("_")[1]
        a, b = random.randint(1, 100), random.randint(1, 100)
        if op == "add":
            a = random.randint(1, 99)
            b = random.randint(1, 100 - a)
            return Question(f"{a}% + {b}% =", f"{a + b}%", category)
        if op == "subtract":
            a, b = max(a, b), min(a, b)
            return Question(f"{a}% - {b}% =", f"{a - b}%", category)
        if op == "multiply":
            if random.choice((True, False)):
                value = Fraction(a * b, 100)
                return Question(f"{a}% x {b}% =", f"{_decimal_text(value)}%", category)
            whole = random.randint(2, 999)
            value = Fraction(a * whole, 100)
            return Question(f"{a}% x {whole} =", _decimal_text(value), category)
        if random.choice((True, False)):
            return Question(f"{a}% ÷ {b}% =", _decimal_text(Fraction(a, b)), category)
        divisor = random.randint(2, 12)
        return Question(f"{a}% ÷ {divisor} =", f"{_decimal_text(Fraction(a, divisor))}%", category)

    if category.startswith("decimal_"):
        op = category.split("_")[1]
        a, b = _random_decimal(), _random_decimal()
        fa, fb = Fraction(a), Fraction(b)
        if op == "add":
            answer = fa + fb
        elif op == "subtract":
            a, b = max(a, b), min(a, b)
            fa, fb = Fraction(a), Fraction(b)
            answer = fa - fb
        elif op == "multiply":
            answer = fa * fb
        else:
            # Keep only exact terminating quotients with at most three decimal places.
            for _ in range(100):
                if fb:
                    candidate = fa / fb
                    denominator = candidate.denominator
                    for prime in (2, 5):
                        while denominator % prime == 0:
                            denominator //= prime
                    if denominator == 1 and max(_decimal_places(candidate), 0) <= 3:
                        answer = candidate
                        break
                b = _random_decimal()
                fb = Fraction(b)
            else:
                # Construct an exact quotient as a safe fallback.
                b = Decimal(random.randint(2, 999)) / Decimal(10)
                q = Decimal(random.randint(1, 999)) / Decimal(100)
                a = b * q
                fa, fb = Fraction(a), Fraction(b)
                answer = Fraction(q)
        symbol = {"add": "+", "subtract": "-", "multiply": "x", "divide": "÷"}[op]
        return Question(f"{a} {symbol} {b} =", _decimal_text(answer, 3 if op == "divide" else 12), category)

    raise ValueError(f"Unknown question category: {category}")


def _decimal_places(value: Fraction) -> int:
    denominator = value.denominator
    places = 0
    while denominator % 2 == 0:
        places += 1
        denominator //= 2
    fives = 0
    while denominator % 5 == 0:
        fives += 1
        denominator //= 5
    return max(places, fives) if denominator == 1 else 999


def make_worksheet(single_category: str) -> tuple[list[Question], list[Question]]:
    """Return 20 questions of the chosen category and 10 mixed questions."""
    if single_category not in set(SINGLE_CATEGORIES.values()):
        raise ValueError("Choose a supported single-operation category")
    single = [generate_question(single_category) for _ in range(20)]
    mixed = [generate_question(random.choice(MIXED_CATEGORIES)) for _ in range(10)]
    return single, mixed
