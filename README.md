# pmail

[![Build Status](https://travis-ci.org/coreygirard/pmail.svg?branch=master)](https://travis-ci.org/coreygirard/pmail) <br>
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black) <br><br>

**THIS IS ALL INACCURATE FOR THE MOMENT**

### Basic usage

```python
gmail = Gmail('tokens.json')
for folder in gmail.get_folders():
    print('\n\nFolder: ' + folder.name)

    for message in folder.get_emails():
        print(message.get_subject())
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
{ "username": "notmyemail@gmail.com", "password": "notmypassword" }
```

`Gmail()` returns an object that can be used to fetch your Gmail folders. `.get_folders()` returns a list of `Folder` objects:

```python
for folder in gmail.get_folders()
```

The `.name` property of a Folder object gives the folder label. To get all emails in a folder, use `.get_emails()`:

```python
for message in folder.get_emails()
```

`Email` objects provide various methods to return the email components:

```
message.get_to()
message.get_from()
message.get_subject()
```

More coming soon!
