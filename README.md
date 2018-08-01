# pmail

### Basic usage

```python
gmail = Gmail('tokens.json')
for folder in gmail.getFolders():
    print('\n\nFolder: ' + folder.name)

    for message in folder.getEmails():
        print(message.getSubject())
```

```
Folder: Important
Top 10 sweaters made from dryer lint
Exclusive adventures to watch paint dry! Act now!

Folder: Unimportant
You are two centuries behind on your rent
One trick to tell if your house is on fire
Is your car cheating on you?
```

#### Explanation

```python
gmail = Gmail(filepath)
```

`filepath` is the path to a JSON file formatted with your Gmail username and password:

```json
{"username": "notmyemail@gmail.com", "password": "notmypassword"}
```

`Gmail()` returns an object that can be used to fetch your Gmail folders. `.getFolders()` returns a list of `Folder` objects:

```python
for folder in gmail.getFolders()
```

The `.name` property of a Folder object gives the folder label. To get all emails in a folder, use `.getEmails()`:
```python
for message in folder.getEmails()
```

`Email` objects provide various methods to return the email components:
```
message.getTo()
message.getFrom()
message.getSubject()
```

More coming soon!


