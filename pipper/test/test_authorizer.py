import pytest


scenarios = [
    ('72s', 72),
    ('85sec', 85),
    ('92Seconds', 92),
    ('1m', 60),
    ('5min', 300),
    ('2MINUTES', 120),
    ('1hr', 3600),
    ('10hrs', 36000),
    ('100hours', 360000)
]


@pytest.mark.parametrize('age,total_seconds')
def to_time_delta(age: str, total_seconds: int):
    """Should convert the age to the expected number of seconds"""