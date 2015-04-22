print "factorial loaded"
import sample.another

def factorial(n):
    if n < 0:
        raise ValueError
    elif n == 0:
        return 1
    else:
        factorial = 1
        for i in range(1, n + 1):
            factorial = factorial * i
        return factorial
