from hypothesis import assume, given
from hypothesis.strategies import text

from src.main import *


def test__clean_folder_name():
    assert clean_folder_name(b'(\\HasNoChildren) "/" "hand_+X"') == "hand_+X"
    assert (
        clean_folder_name(b'(\\HasNoChildren \\Trash) "/" "[Gmail]/Trash"')
        == "[Gmail]/Trash"
    )


@given(text(), text())
def test__clean_folder_name__property(a, b):
    assume('"' not in a)
    assume('"' not in b)

    before = (a + '"' + b + '"').encode("utf-8")
    after = b

    assert clean_folder_name(before) == after
