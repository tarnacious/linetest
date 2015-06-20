from sample.factorial import factorial
from unittest import TestCase


class FactorialTestCase(TestCase):

    def test_factorial_0(self):
        assert factorial(0) == 1


    def test_factorial_1(self):
        assert factorial(1) == 1

    def test_factorial_7(self):
        assert factorial(7) == 5040

    def test_factorial_negative(self):
        self.assertRaises(ValueError, factorial, -1)
