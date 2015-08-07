import random
from datetime import timedelta


def random_set_with(length, mean):
    s = [mean] * length
    for i in range(0, 1000):
        i1 = random.randint(0, length - 1)
        i2 = random.randint(0, length - 1)
        randomizer = random.random()
        old_val = s[i1]
        s[i1] = old_val * randomizer
        difference = old_val - s[i1]
        s[i2] += difference

    return s


def random_timestamp(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)
