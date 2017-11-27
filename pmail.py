import smtplib
import time
import imaplib
import email
import json

from pprint import pprint

server,port = "imap.gmail.com",993

class Email(object):
    def __init__(self,data):
        self.msg = email.message_from_string(data[0][1].decode('utf-8'))

    def prettyFrom(self):
        return email.utils.parseaddr(self.msg['From'])

    def __repr__(self):
        return "Email('" + str(self.prettyFrom()[1]) + "', '" + str(self.msg['Subject']) + "')"

class Folder(object):
    def __init__(self,m,name):
        self.m = m
        self.name = name

    def fetchMail(self):
        _, data = self.m.select(self.name)
        _, data = self.m.uid('search',None,'ALL')

        for num in data[0].split():
            try:
                _, data = self.m.uid('fetch',num,'(RFC822)')
                yield Email(data)
            except:
                pass

    def getMail(self,stream=False):
        if stream:
            for f in self.fetchMail():
                yield f
        else:
            return list(self.fetchMail())


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



g = Gmail('tokens.json')
f = g.getFolders()

for m in f['++'].getMail(stream=True):
    print(m)

#f.name = '++'
#print(f.getMail())





