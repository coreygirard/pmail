import smtplib
import time
import imaplib
import email
import json


server,port = "imap.gmail.com",993

class Folder(object):
    def __init__(self,m,name):
        self.m = m
        self.name = name

    def getMail(self):
        _, data = self.m.select(self.name)
        a,b = self.m.search(None,'ALL')
        return b

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

    def getFolders(self):
        _, folders = self.m.list()
        temp = []
        for f in folders:
            name = f.decode('utf-8')
            name = list(name)
            del name[-1]
            while '"' in name:
                del name[0]
            name = ''.join(name)

            if '[Gmail]' not in name:
                temp.append(Folder(self.m,name))
        return temp



g = Gmail('tokens.json')
for f in g.getFolders():
    print(f.name)
    print(f.getMail())

#f.name = '++'
#print(f.getMail())
