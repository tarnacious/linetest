import factorial
print "WOOT"
print factorial.factorial


from factorial import factorial


def test_factorial_0():
    assert factorial(0) == 1


def test_factorial_1():
    assert factorial(1) == 1


def test_factorial_7():
    assert factorial(7) == 5040
