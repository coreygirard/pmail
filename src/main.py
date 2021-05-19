import base64
import email
import imaplib
import json
import quopri
import re
import smtplib
import time
from pprint import pprint

import pendulum

server, port = "imap.gmail.com", 993

encoded_word_regex = r"=[?](.*?)[?]([BbQq])[?](.*?)[?]="
# from https://dmorgan.info/posts/encoded-word-syntax/
# (heavily modified)
def _encoded_words_to_text(encoded_words):
    match = re.match(encoded_word_regex, encoded_words)

    if match is None:
        return encoded_words

    try:
        charset, encoding, encoded_text = match.groups()

        if charset.upper() != "UTF-8":
            raise ValueError("Can't handle encodings other than UTF-8")

        if encoding.upper() == "B":
            byte_string = base64.b64decode(encoded_text)
        elif encoding.upper() == "Q":
            byte_string = quopri.decodestring(encoded_text)
        return byte_string.decode(charset)
    except:
        return ("ERROR", encoded_words)


def _decode_encoded_chunks(msg):
    """Splits input text into chunks of encoded text and unencoded text,
    then decodes the encoded text and concatenates all chunks"""

    encoded_word_regex_captureall = (
        "(" + encoded_word_regex.replace("(", "").replace(")", "") + ")"
    )

    out = ""
    for s in re.split(encoded_word_regex_captureall, msg):
        if re.fullmatch(encoded_word_regex, s):
            out += _encoded_words_to_text(s)
        else:
            out += s
    return out


def _decode(something):
    if isinstance(something, list):
        return list(map(_decode_encoded_chunks, something))
    elif isinstance(something, tuple):
        return tuple(map(_decode_encoded_chunks, something))
    elif isinstance(something, str):
        return _decode_encoded_chunks(something)

    raise TypeError("Can only decode lists of strings, tuples of strings, or strings")


def _strip_newlines(something):
    return re.sub(r"[ ]*((\r\n|\r|\n)+[ ]*)+", " ", something)


def _process(something):
    something = _decode(something)
    something = _strip_newlines(something)
    return something


def clean_folder_name(f):
    name = f.decode("utf-8")

    name = list(name)
    del name[-1]
    while '"' in name:
        del name[0]
    name = "".join(name)

    return name


def connect(username, password):
    conn = imaplib.IMAP4_SSL(server)
    conn.login(username, password)
    return {"connection": conn, "username": username, "password": password}


def get_folders(conn):
    _, folders = conn["connection"].list()
    for f in folders:
        name = clean_folder_name(f)
        if "[Gmail]" in name:
            continue
        yield name


def _get_body(msg):
    maintype = msg.get_content_maintype()
    if maintype == "multipart":
        for part in msg.get_payload():
            if part.get_content_maintype() == "text":
                return part.get_payload()
        return []  # TODO: sometimes doesn't find any text
    elif maintype == "text":
        return msg.get_payload()


def _get_to(msg):
    return _decode(msg["To"])


def _get_from(msg):
    return _decode(msg["From"])


def _get_subject(msg):
    return _decode(msg["Subject"])


def _get_pretty_to(msg):
    return _decode(email.utils.parseaddr(msg["to"]))


def _get_pretty_from(msg):
    return _decode(email.utils.parseaddr(msg["from"]))


def _pendulum_to_dict(dt):
    return {
        "year": dt.year,
        "month": dt.month,
        "day": dt.day,
        "hour": dt.hour,
        "minute": dt.minute,
        "second": dt.second,
        "ms": dt.microsecond / 1000,
        "day_of_week": dt.day_of_week,
        "day_of_year": dt.day_of_year,
        "week_of_month": dt.week_of_month,
        "week_of_year": dt.week_of_year,
        "timestamp": dt.float_timestamp,
        "string": dt.format("YYYY-MM-DD HH:mm:ss ZZ"),
    }


def _get_date(msg):
    for format in [
        "ddd, DD MMM YYYY HH:mm:ss ZZ",
        "DD MMM YYYY HH:mm:ss ZZ",
        "ddd, DD MMM YYYY HH:mm:ss zz",
        "DD MMM YYYY HH:mm:ss zz",
    ]:
        try:
            dt = pendulum.from_format(msg["Date"], format)
            return _pendulum_to_dict(dt)
        except:
            pass

    raise ValueError(f"Unrecognized date format: {msg['Date']}")


def get_mail(conn, folder, limit=None):
    conn["connection"].select(folder)
    _, (data, *_) = conn["connection"].uid("search", None, "ALL")
    data = data.split()
    if limit is not None:
        data = data[:limit]

    for num in data:
        try:
            _, msg = conn["connection"].uid("fetch", num, "(RFC822)")
            msg = email.message_from_string(msg[0][1].decode("utf-8"))
            data = {
                "to": _get_to(msg),
                "from": _get_from(msg),
                "subject": _get_subject(msg),
                "pretty_to": _get_pretty_to(msg),
                "pretty_from": _get_pretty_from(msg),
                "body": _get_body(msg),
                "date": _get_date(msg),
            }
            yield data
        except Exception as e:
            print(repr(e))
            try:
                print(msg["Date"])
            except:
                pass
            print("\n")
            conn = connect(conn["username"], conn["password"])
            conn["connection"].select(folder)
