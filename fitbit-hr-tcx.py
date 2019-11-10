#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from termcolor import cprint
except ImportError:
    # status messages won't look as cool
    pass
import json
from pprint import pprint
import sys

from fitbit_hr_tcx.activity import Activity
from fitbit_hr_tcx.oauth2server import OAuth2Server

DEFAULT_CLIENT_FILE = ".fitbit.client"


def eprint(*args, **kwargs):
    if "termcolor" in sys.modules:
        cprint(*args, file=sys.stderr, **kwargs)
    else:
        kwargs.pop("attrs", None)
        print(*args, file=sys.stderr, **kwargs)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"{__file__} <tcx-file> [client-file]")
        sys.exit(1)

    try:
        client_file = sys.argv[2]
    except IndexError:
        eprint(f"Using default client file '{DEFAULT_CLIENT_FILE}'")
        client_file = DEFAULT_CLIENT_FILE
    with open(client_file) as f:
        client = json.load(f)

    server = OAuth2Server(client["id"], client["secret"])
    activity = Activity(sys.argv[1])

    hr = activity.get_heart_rate(server)
    if not hr:
        eprint(
            "Didn't get no heart rates. Try syncing your fitbit? 🌀☁️ ",
            "yellow",
            attrs=["bold"],
        )
        sys.exit(1)

    activity.merge_heart_rate(hr)

    try:
        print(activity.xml.toxml())
    except AttributeError:
        import sys
        sys.path.append("/Users/oliver/repos/fit")
        import fit
        from fit import FitFile
        with FitFile.open("copy.fit", mode="w") as fout:
            fout.copy(activity.fit)

    eprint("All done! 💞✨", attrs=["bold"])
