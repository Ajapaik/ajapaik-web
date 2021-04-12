from ajapaik.ajapaik.utils import get_pagination_parameters


def test_least_frequent():
    assert get_pagination_parameters(0, 50, 500) == (0, 50, 500, 10, 0)
    assert get_pagination_parameters(5, 50, 500) == (200, 250, 500, 10, 5)
    assert get_pagination_parameters(27, 5, 500) == (130, 135, 500, 100, 27)
    assert get_pagination_parameters(5, 500, 500) == (0, 500, 500, 1, 1)
