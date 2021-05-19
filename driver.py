import json
import os
from pprint import pprint

import more_itertools

from src.main import connect, get_folders, get_mail


def get_creds():
    with open("creds.json", "r") as f:
        data = json.load(f)
    return data["username"], data["password"]


def write_json_stream(filename, s):
    with open(filename, "w") as f:
        f.write("[\n")
        for i, e in enumerate(s):
            if not i % 100 and i > 0:
                print(f"wrote {i} emails")

            f.write(json.dumps(e, indent=4) + ",\n")

    with open(filename, "rb+") as f:
        # remove trailing ",\n", because we are at final list element
        f.seek(-2, os.SEEK_END)
        f.truncate()

        # close list
        f.write("\n]\n".encode("utf-8"))


if __name__ == "__main__":
    conn = connect(*get_creds())
    # pprint(list(get_folders(conn)))

    stream = get_mail(conn, "all_mail")
    for i, s in enumerate(more_itertools.chunked(stream, 100)):
        filepath = f"data/output_{i}.json"
        print(f"\n\nwriting to {filepath}")
        write_json_stream(filepath, s)
