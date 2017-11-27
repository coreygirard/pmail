import smtplib
import time
import imaplib
import email
import json
import re

from pprint import pprint

server,port = "imap.gmail.com",993

class Email(object):
    def __init__(self,data):
        self.msg = email.message_from_string(data[0][1].decode('utf-8'))

    def getTo(self):
        return self.msg['To']

    def prettyTo(self):
        return email.utils.parseaddr(self.getTo())

    def getFrom(self):
        return self.msg['From']

    def prettyFrom(self):
        return email.utils.parseaddr(self.getFrom)

    def getSubject(self):
        return self.msg['Subject']

    def getBody(self):
        maintype = self.msg.get_content_maintype()
        if maintype == 'multipart':
            for part in self.msg.get_payload():
                if part.get_content_maintype() == 'text':
                    return part.get_payload()
        elif maintype == 'text':
            return self.msg.get_payload()

    # TODO: implement returning only the visible text of the message body
    #def prettyBody(self):

    def __repr__(self):
        return "Email('" + str(self.prettyFrom()[1]) + "', '" + str(self.msg['Subject']) + "')"

class Folder(object):
    def __init__(self,m,name):
        self.m = m
        self.name = name

    def fetchMailStream(self,limit):
        _, data = self.m.select(self.name)
        _, data = self.m.uid('search',None,'ALL')

        for num in data[0].split()[:limit]:
            try:
                _, data = self.m.uid('fetch',num,'(RFC822)')
                yield Email(data)
            except:
                pass

    def fetchMail(self,limit):
        return list(self.fetchMailStream(limit))

    def getMail(self,limit=None,stream=False):
        if stream:
            return self.fetchMailStream(limit)
        else:
            return self.fetchMail(limit)


class Gmail(object):
    def __init__(self,auth):
        try:
            temp = json.load(auth)
        except:
            if type(auth) == type('string'):
                with open('tokens.json') as f:
                    temp = json.load(f)
            elif type(auth) == type(dict()):
                temp = auth

        self.username = temp['username']
        self.password = temp['password']


        self.m = imaplib.IMAP4_SSL(server)
        self.m.login(self.username,self.password)

    def cleanFolderName(self,f):
        name = f.decode('utf-8')

        name = list(name)
        del name[-1]
        while '"' in name:
            del name[0]
        name = ''.join(name)

        return name

    def getFolders(self):
        _, folders = self.m.list()
        temp = {}
        for f in folders:
            name = self.cleanFolderName(f)
            if '[Gmail]' not in name:
                temp[name] = Folder(self.m,name)
        return temp



