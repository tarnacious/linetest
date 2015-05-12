#from sample.subsample.add import add
import sample.subsample.add


def test_add():
    assert sample.subsample.add.add(2, 2) == 4
