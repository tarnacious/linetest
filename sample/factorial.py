print "factorial loaded", "cat dog"
print "load2"
import sample.another

sample.another.prn("KATZE")

def factorial(n):

    if n < 0:
        raise ValueError

    if n == 0:
        return 1

    factorial = 1
    for i in range(1, n + 1):
        factorial = factorial * i
    return factorial

a = 1
print "factorial finished loading"
print "factorial finished loading"
print "factorial finished loading"
