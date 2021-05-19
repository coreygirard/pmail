import base64
import quopri

from hypothesis import assume, given
from hypothesis.strategies import text

from src.main import (_decode, _encoded_words_to_text, _strip_newlines,
                      clean_folder_name)


# https://dmorgan.info/posts/encoded-word-syntax/
def _text_to_encoded_words(text, charset, encoding):
    """
    text: text to be transmitted
    charset: the character set for text
    encoding: either 'q' for quoted-printable or 'b' for base64
    """
    byte_string = text.encode(charset)
    if encoding.lower() == "b":
        encoded_text = base64.b64encode(byte_string)
    elif encoding.lower() == "q":
        encoded_text = quopri.encodestring(byte_string)
    return "=?{charset}?{encoding}?{encoded_text}?=".format(
        charset=charset.upper(),
        encoding=encoding.upper(),
        encoded_text=encoded_text.decode("ascii"),
    )


def test___decode():
    before = """The Post Most: Niagara Falls is coated in ice\r\n =?UTF-8?Q?=E2=80=94?= and absolutely jaw-dropping"""
    after = _decode(before)

    assert after.startswith("""The Post Most: Niagara Falls is coated in ice\r\n """)
    assert after.endswith(""" and absolutely jaw-dropping""")

    assert len(after) == len(
        """The Post Most: Niagara Falls is coated in ice\r\n """
    ) + 1 + len(""" and absolutely jaw-dropping""")

    # Just a dog emoji
    before = b"\xf0\x9f\x90\xb6".decode("utf-8")
    # after = _decode(before)
    # assert after == "wrong"


def test___strip_newlines():
    before = """test this"""
    after = "test this"
    assert _strip_newlines(before) == after

    before = """test \n this"""
    after = "test this"
    assert _strip_newlines(before) == after

    before = """test\r\nthis"""
    after = "test this"
    assert _strip_newlines(before) == after

    before = """test \n\n\n\n\n this"""
    after = "test this"
    assert _strip_newlines(before) == after


@given(text(), text("\n\r "), text())
def test___strip_newlines__property(a, b, c):
    a = a.rstrip()
    c = c.lstrip()

    assume("\n" not in a and "\r" not in a)
    assume("\n" in b or "\r" in b)
    assume("\n" not in c and "\r" not in c)

    before = a + b + c
    after = a + " " + c

    assert _strip_newlines(before) == after


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
