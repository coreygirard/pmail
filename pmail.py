import smtplib
import time
import imaplib
import email
import json
import re


from pprint import pprint

server, port = "imap.gmail.com", 993

class Email(object):
    def __init__(self, data):
        self.msg = email.message_from_string(data[0][1].decode('utf-8'))

    def get_to(self):
        return self.msg['To']

    def pretty_to(self):
        return email.utils.parseaddr(self.get_to())

    def get_from(self):
        return self.msg['From']

    def pretty_from(self):
        return email.utils.parseaddr(self.get_from)

    def get_subject(self):
        return self.msg['Subject']

    def get_body(self):
        maintype = self.msg.get_content_maintype()
        if maintype == 'multipart':
            for part in self.msg.get_payload():
                if part.get_content_maintype() == 'text':
                    return part.get_payload()
        elif maintype == 'text':
            return self.msg.get_payload()

    # TODO: implement returning only the visible text of the message body
    #def pretty_body(self):

    def __repr__(self):
        return "Email('" + str(self.pretty_from()[1]) + "', '" + str(self.msg['Subject']) + "')"

class Folder(object):
    def __init__(self, m, name):
        self.m = m
        self.name = name

    def fetch_mail_stream(self, limit):
        _, data = self.m.select(self.name)
        _, data = self.m.uid('search', None, 'ALL')

        for num in data[0].split()[:limit]:
            try:
                _, data = self.m.uid('fetch', num, '(RFC822)')
                yield Email(data)
            except:
                pass

    def fetch_mail(self, limit):
        return list(self.fetch_mail_stream(limit))

    def get_mail(self, limit=None, stream=False):
        if stream:
            return self.fetch_mail_stream(limit)
        else:
            return self.fetch_mail(limit)


class Gmail(object):
    def __init__(self, auth):
        try:
            temp = json.load(auth)
        except:
            if isinstance(auth, str):
                with open('tokens.json') as f:
                    temp = json.load(f)

            elif isinstance(auth, dict):
                temp = auth

        self.username = temp['username']
        self.password = temp['password']

        self.m = imaplib.IMAP4_SSL(server)
        self.m.login(self.username, self.password)

    def clean_folder_name(self, f):
        name = f.decode('utf-8')

        name = list(name)
        del name[-1]
        while '"' in name:
            del name[0]
        name = ''.join(name)

        return name

    def get_folders(self):
        _, folders = self.m.list()
        temp = {}
        for f in folders:
            name = self.clean_folder_name(f)
            if '[Gmail]' not in name:
                temp[name] = Folder(self.m, name)
        return temp
