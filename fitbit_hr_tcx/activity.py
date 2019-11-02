#!/usr/bin/env python
# -*- coding: utf-8 -*-
from xml.dom import minidom
from datetime import datetime, tzinfo
from dateutil import tz


class Activity:
    def __init__(self, tcx_file: str):
        """ Initialize the Activity. """
        self._xml = minidom.parse(tcx_file)

        times = self._xml.getElementsByTagName("Time")
        times = [times[0], times[-1]]
        start, end = [t.childNodes[0].data for t in times]

        self._start = datetime.fromisoformat(start)
        self._end = datetime.fromisoformat(end)

    def start(self, timezone: tzinfo = tz.tzlocal()) -> datetime:
        """ Get the start of the activity. """
        return self._start.astimezone(timezone)

    def end(self, timezone: tzinfo = tz.tzlocal()) -> datetime:
        """ Get the end of the activity. """
        return self._end.astimezone(timezone)
