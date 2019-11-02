#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
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

    hr = server.fitbit.intraday_time_series(
        "activities/heart",
        base_date=activity.start(),
        detail_level="1sec",
        start_time=activity.start(),
        end_time=activity.end(),
    )["activities-heart-intraday"]["dataset"]

    pprint(hr)
