from unittest import TestCase
import numpy as np

from permutate import get_perms


class Test(TestCase):

    def test_get_perms(self):
        result = get_perms(range(3))
        self.assertTrue(np.array_equiv(result, [[0, 1, 2], [0, 2, 1], [1, 0, 2],
                                                [1, 2, 0], [2, 0, 1], [2, 1, 0]]))

