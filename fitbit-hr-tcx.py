#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import dateutil
import dateutil.tz
import json
from pprint import pprint
import sys
from xml.dom import minidom

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

    xmldoc = minidom.parse(sys.argv[1])
    times = xmldoc.getElementsByTagName("Time")
    times = [times[0], times[-1]]
    start, end = [t.childNodes[0].data for t in times]

    server = OAuth2Server(client["id"], client["secret"])

    as_local = lambda dt: datetime.fromisoformat(dt).astimezone(dateutil.tz.tzlocal())
    hr = server.fitbit.intraday_time_series(
        "activities/heart",
        base_date=as_local(start),
        detail_level="1sec",
        start_time=as_local(start),
        end_time=as_local(end),
    )["activities-heart-intraday"]["dataset"]

    pprint(hr)
