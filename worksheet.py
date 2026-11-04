"""Question generation for the Daily Practice worksheet."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, timedelta
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
    "文字应用题": "word_problems",
    "时间日期应用题": "time_date_word_problems",
    "二维和三维图形应用题": "shape_word_problems",
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


def _word_problem_question() -> Question:
    """Generate a one-step counting or perimeter/area word problem."""
    problem_type = random.choice((
        "animal_legs", "animal_total", "people_difference",
        "rectangle_area", "rectangle_side_from_area", "square_area",
        "square_side_from_area", "square_side_from_perimeter",
        "rectangle_side_from_perimeter", "same_perimeter_square",
        "same_perimeter_rectangle", "same_area_square",
    ))

    if problem_type == "animal_legs":
        total = random.randint(12, 40)
        rabbits = random.randint(2, total - 2)
        chickens = total - rabbits
        legs = 2 * chickens + 4 * rabbits
        if random.choice((True, False)):
            prompt = f"There are {total} chickens and rabbits. They have {legs} legs altogether. How many rabbits are there?"
            answer = f"{rabbits} rabbits"
        else:
            prompt = f"There are {total} chickens and rabbits. They have {legs} legs altogether. How many chickens are there?"
            answer = f"{chickens} chickens"
    elif problem_type == "animal_total":
        rabbits, chickens = random.randint(2, 15), random.randint(2, 25)
        legs = 2 * chickens + 4 * rabbits
        prompt = f"A farm has {rabbits} rabbits and some chickens. The animals have {legs} legs altogether. How many animals are there?"
        answer = str(rabbits + chickens)
    elif problem_type == "people_difference":
        girls = random.randint(6, 24)
        difference = random.randint(1, min(12, girls))
        boys = girls + difference
        total = boys + girls
        prompt = f"A class has {total} students. There are {difference} more boys than girls. How many boys and girls are there?"
        answer = f"{boys} boys and {girls} girls"
    elif problem_type == "rectangle_area":
        length, width = random.randint(8, 30), random.randint(4, 18)
        prompt = f"A rectangle is {length} cm long and {width} cm wide. What is its area?"
        answer = f"{length * width} cm²"
    elif problem_type == "rectangle_side_from_area":
        width, length = random.randint(3, 15), random.randint(4, 18)
        area = width * length
        prompt = f"A rectangle has an area of {area} cm² and a length of {length} cm. What is its width?"
        answer = f"{width} cm"
    elif problem_type == "square_area":
        side = random.randint(4, 20)
        prompt = f"A square has a side length of {side} cm. What is its area?"
        answer = f"{side * side} cm²"
    elif problem_type == "square_side_from_area":
        side = random.randint(4, 20)
        prompt = f"A square has an area of {side * side} cm². What is its side length?"
        answer = f"{side} cm"
    elif problem_type == "square_side_from_perimeter":
        side = random.randint(4, 25)
        prompt = f"A square has a perimeter of {4 * side} cm. What is its side length?"
        answer = f"{side} cm"
    elif problem_type == "rectangle_side_from_perimeter":
        length, width = random.randint(8, 30), random.randint(3, 15)
        prompt = f"A rectangle has a perimeter of {2 * (length + width)} cm and a length of {length} cm. What is its width?"
        answer = f"{width} cm"
    elif problem_type == "same_perimeter_square":
        length, width = random.randrange(8, 31, 2), random.randrange(4, 21, 2)
        square_side = (length + width) // 2
        prompt = f"A square has the same perimeter as a {length} cm by {width} cm rectangle. What is the square's side length?"
        answer = f"{square_side} cm"
    elif problem_type == "same_perimeter_rectangle":
        square_side = random.randint(8, 24)
        length = random.randint(3, 2 * square_side - 3)
        width = 2 * square_side - length
        prompt = f"A rectangle has the same perimeter as a square with side {square_side} cm. If its length is {length} cm, what is its width?"
        answer = f"{width} cm"
    else:
        square_side = random.randrange(6, 31, 2)
        length, width = 2 * square_side, square_side // 2
        prompt = f"A square has the same area as a {length} cm by {width} cm rectangle. What is the square's side length?"
        answer = f"{square_side} cm"

    return Question(prompt, answer, "word_problems")


def _clock_text(minutes: int) -> str:
    hour, minute = divmod(minutes, 60)
    suffix = "am" if hour < 12 else "pm"
    display_hour = hour % 12 or 12
    return f"{display_hour}:{minute:02d} {suffix}"


def _duration_text(minutes: int) -> str:
    hours, remaining_minutes = divmod(minutes, 60)
    parts = []
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if remaining_minutes:
        parts.append(f"{remaining_minutes} minute{'s' if remaining_minutes != 1 else ''}")
    return " and ".join(parts)


def _date_text(value: date) -> str:
    return f"{value.day} {value.strftime('%B')}"


def _time_date_word_problem() -> Question:
    """Generate a practical elapsed-time, calendar, or age problem."""
    problem_type = random.choice((
        "daily_schedule", "event_duration", "days_in_weeks",
        "days_until_birthday", "birthday_gap", "age_ratio_future",
        "age_sum_ratio_future", "age_difference_future",
    ))

    if problem_type == "daily_schedule":
        name = random.choice(("Mia", "Noah", "Lily", "Ethan", "Ava"))
        start = random.randint(6 * 60 + 30, 9 * 60)
        travel_to = random.randrange(10, 36, 5)
        first_activity = random.randrange(45, 121, 5)
        break_time = random.choice((0, 10, 15, 20, 30))
        second_activity = random.randrange(45, 121, 5)
        travel_home = random.randrange(10, 36, 5)
        first, second = random.choice((
            ("choir rehearsal", "basketball practice"),
            ("basketball practice", "the cinema"),
            ("choir rehearsal", "the cinema"),
        ))
        end = start + travel_to + first_activity + break_time + second_activity + travel_home
        break_sentence = (
            f"{name} takes a break of {_duration_text(break_time)} between them. "
            if break_time else f"{name} has no break between the activities. "
        )
        prompt = (
            f"{name} leaves home at {_clock_text(start)}. The trip to {first} takes "
            f"{_duration_text(travel_to)}. {name} spends {_duration_text(first_activity)} at {first}. "
            f"{break_sentence}{name} then spends {_duration_text(second_activity)} at {second} "
            f"and travels home for {_duration_text(travel_home)}. What time do they get home?"
        )
        answer = _clock_text(end)
    elif problem_type == "event_duration":
        start = random.randint(8 * 60, 17 * 60)
        duration = random.randrange(35, 241, 5)
        event = random.choice(("a basketball game", "a movie", "a choir concert"))
        prompt = f"{event.capitalize()} starts at {_clock_text(start)} and finishes at {_clock_text(start + duration)}. How long does it last?"
        answer = _duration_text(duration)
    elif problem_type == "days_in_weeks":
        weeks, extra_days = random.randint(2, 6), random.randint(1, 6)
        prompt = f"A holiday lasts {weeks} weeks and {extra_days} days. How many days is that altogether?"
        answer = str(weeks * 7 + extra_days)
    elif problem_type == "days_until_birthday":
        today = random.choice((date(2027, 2, 27), date(2027, 5, 12), date(2027, 9, 21)))
        days_left = random.choice((7, 10, 14, 21, 30, 45))
        birthday = today + timedelta(days=days_left)
        prompt = f"Today is {_date_text(today)}. {random.choice(('Sam', 'Ella', 'Oliver'))}'s birthday is {_date_text(birthday)}. How many days are left until the birthday?"
        answer = str(days_left)
    elif problem_type == "birthday_gap":
        first_birthday = date(2027, 1, 1) + timedelta(days=random.randint(0, 319))
        gap = random.randint(3, 20)
        second_birthday = first_birthday + timedelta(days=gap)
        prompt = (
            f"Two brothers have birthdays on {_date_text(first_birthday)} and "
            f"{_date_text(second_birthday)} in the same year. How many days apart are their birthdays?"
        )
        answer = str(gap)
    elif problem_type == "age_ratio_future":
        younger = random.randint(5, 14)
        multiple = random.randint(2, 4)
        older = younger * multiple
        years_ahead = random.choice((5, 10))
        prompt = (
            f"Kai is {multiple} times as old as his younger brother Max. Max is {younger} years old. "
            f"How old will each brother be in {years_ahead} years, and what will their ages add up to?"
        )
        answer = (
            f"Max: {younger + years_ahead} years; Kai: {older + years_ahead} years; "
            f"total: {younger + older + 2 * years_ahead} years"
        )
    elif problem_type == "age_sum_ratio_future":
        younger = random.randint(5, 12)
        multiple = random.randint(2, 4)
        older = younger * multiple
        total_now = younger + older
        years_ahead = random.choice((5, 10))
        prompt = (
            f"Two brothers' ages add up to {total_now} years. The older brother is {multiple} times "
            f"as old as the younger one. How old will each be in {years_ahead} years?"
        )
        answer = f"Younger: {younger + years_ahead} years; older: {older + years_ahead} years"
    else:
        younger = random.randint(4, 15)
        multiple = random.randint(2, 4)
        older = younger * multiple
        years_apart = older - younger
        years_ahead = random.choice((5, 10))
        prompt = (
            f"An older brother is {multiple} times as old as his younger brother and is "
            f"{years_apart} years older. How old will the younger brother be in {years_ahead} years?"
        )
        answer = f"{younger + years_ahead} years old"

    return Question(prompt, answer, "time_date_word_problems")


def _shape_word_problem() -> Question:
    """Generate a geometry vocabulary or properties word problem."""
    polygon_names = {
        3: "triangle", 4: "quadrilateral", 5: "pentagon", 6: "hexagon",
        7: "heptagon", 8: "octagon", 9: "nonagon", 10: "decagon",
    }
    shape_type = random.choice((
        "polygon_name", "polygon_sides", "polygon_vertices", "polygon_angles",
        "solid_name", "solid_faces", "solid_edges", "solid_vertices",
    ))

    if shape_type.startswith("polygon"):
        sides = random.randint(3, 10)
        # Four-sided polygons include familiar rectangle and square names.
        if sides == 4:
            name = random.choice(("rectangle", "square", "quadrilateral"))
        else:
            name = polygon_names[sides]
        if shape_type == "polygon_name":
            if name == "square":
                prompt = "A flat shape has 4 equal sides and 4 right angles. What is its name?"
            elif name == "rectangle":
                prompt = "A flat shape has 4 right angles and two different side lengths. What is its name?"
            else:
                prompt = f"A flat shape has {sides} straight sides. What is its name?"
            answer = name
        elif shape_type == "polygon_sides":
            article = "an" if name[0].lower() in "aeiou" else "a"
            prompt = f"How many sides does {article} {name} have?"
            answer = str(sides)
        elif shape_type == "polygon_vertices":
            article = "an" if name[0].lower() in "aeiou" else "a"
            prompt = f"How many vertices (corners) does {article} {name} have?"
            answer = str(sides)
        else:
            article = "an" if name[0].lower() in "aeiou" else "a"
            prompt = f"How many interior angles does {article} {name} have?"
            answer = str(sides)
    else:
        solids = {
            "cube": (6, 12, 8),
            "rectangular prism": (6, 12, 8),
            "triangular prism": (5, 9, 6),
            "square-based pyramid": (5, 8, 5),
            "triangular pyramid": (4, 6, 4),
        }
        name = random.choice(tuple(solids))
        faces, edges, vertices = solids[name]
        if shape_type == "solid_name":
            descriptions = {
                "cube": "6 equal square faces",
                "rectangular prism": "6 rectangular faces, with some side lengths different",
                "triangular prism": "2 triangular faces and 3 rectangular faces",
                "square-based pyramid": "1 square face and 4 triangular faces",
                "triangular pyramid": "4 triangular faces",
            }
            prompt = f"A solid has {descriptions[name]}. What is its name?"
            answer = name
        elif shape_type == "solid_faces":
            prompt = f"How many faces does a {name} have?"
            answer = str(faces)
        elif shape_type == "solid_edges":
            prompt = f"How many edges does a {name} have?"
            answer = str(edges)
        else:
            prompt = f"How many vertices (corners) does a {name} have?"
            answer = str(vertices)

    return Question(prompt, answer, "shape_word_problems")


def generate_question(category: str) -> Question:
    """Generate one exact, one-step arithmetic question."""
    if category == "unit_conversion":
        return _unit_conversion_question()
    if category == "word_problems":
        return _word_problem_question()
    if category == "time_date_word_problems":
        return _time_date_word_problem()
    if category == "shape_word_problems":
        return _shape_word_problem()

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
