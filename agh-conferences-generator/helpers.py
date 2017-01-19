import random
from math import floor

import numpy as np

random_part = lambda x: x[random.randint(0, len(x) - 1)]

def fixed_mean_random(mean, difference, size):
    return [
        int(round(value, 0)) if int(value) != 0 else 1
        for value in np.random.normal(mean, difference, size)
    ]