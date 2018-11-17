import email
import imaplib
import json
import re
import smtplib
import time
from pprint import pprint

server, port = "imap.gmail.com", 993


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
    return conn


def get_folders(conn):
    _, folders = conn.list()
    for f in folders:
        print(f)
        name = clean_folder_name(f)
        print(name)
        if "[Gmail]" in name:
            continue
        yield name


def get_body(msg):
    maintype = msg.get_content_maintype()
    if maintype == "multipart":
        for part in msg.get_payload():
            if part.get_content_maintype() == "text":
                return part.get_payload()
    elif maintype == "text":
        return msg.get_payload()


def get_mail(conn, folder, limit=None):
    conn.select(folder)
    _, (data, *_) = conn.uid("search", None, "ALL")
    data = data.split()
    if limit is not None:
        data = data[:limit]

    for num in data:
        try:
            _, msg = conn.uid("fetch", num, "(RFC822)")
            msg = email.message_from_string(msg[0][1].decode("utf-8"))
            data = {
                "to": msg["To"],
                "from": msg["From"],
                "subject": msg["Subject"],
                "pretty_to": email.utils.parseaddr(msg["to"]),
                "pretty_from": email.utils.parseaddr(msg["from"]),
                "body": get_body(msg)[:50],
            }
            yield data
        except:
            pass
