import pytest


class RetainedObject:
    live = 0

    def __init__(self):
        type(self).live += 1

    def __del__(self):
        type(self).live -= 1


def test_empty():
    pass


@pytest.mark.parametrize("value", range(100))
def test_parametrized(value):
    assert value >= 0


class TestXunitStyle:
    def setup_method(self):
        self.obj = RetainedObject()

    def test_instance_object(self):
        assert self.obj is not None
