#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from pprint import pprint
import sys

from fitbit_hr_tcx.activity import Activity
from fitbit_hr_tcx.oauth2server import OAuth2Server

DEFAULT_CLIENT_FILE = ".fitbit.client"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"{__file__} <tcx-file> [client-file]")
        sys.exit(1)

    try:
        client_file = sys.argv[2]
    except IndexError:
        print(f"Using default client file '{DEFAULT_CLIENT_FILE}'")
        client_file = DEFAULT_CLIENT_FILE
    with open(client_file) as f:
        client = json.load(f)

    server = OAuth2Server(client["id"], client["secret"])
    activity = Activity(sys.argv[1])

    hr = activity.get_heart_rate(server)
    activity.merge_heart_rate(hr)
    print(activity.xml.toxml())
