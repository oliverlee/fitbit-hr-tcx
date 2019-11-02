#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, time, tzinfo
from dateutil import tz
from statistics import mean
from typing import List, Optional
from xml.dom import minidom

from fitbit_hr_tcx.oauth2server import OAuth2Server


class HeartRateSample:
    def __init__(self, sample_time: datetime, bpm: int):
        """ Initialize the HeartRateSample. """
        self.sample_time = sample_time
        self.bpm = bpm

        # Save this so we don't keep calculating it each time
        self.sample_time_isoformat = sample_time.isoformat()

    def __eq__(self, other):
        """ Compare sample time of self and other for equality. """
        if isinstance(other, HeartRateSample):
            return self.sample_time == self.sample_time
        elif isinstance(other, minidom.Element):
            return self.sample_time_isoformat == other.childNodes[0].data

    def __lt__(self, other):
        """ Check if sample time of self is less than sample time of other. """
        if isinstance(other, HeartRateSample):
            return self.sample_time < self.sample_time
        elif isinstance(other, minidom.Element):
            return self.sample_time_isoformat < other.childNodes[0].data

    def __str__(self):
        """ Return a string representation of a HeartRateSample. """
        return f"({str(self.sample_time_isoformat)}, {self.bpm})"


class Activity:
    def __init__(self, tcx_file: str):
        """ Initialize the Activity. """
        self.xml = minidom.parse(tcx_file)

        times = self.xml.getElementsByTagName("Time")
        self.times = times

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

    def get_heart_rate(self, server: OAuth2Server) -> List[HeartRateSample]:
        """ Get the heart rate during the activity. """
        start = self.start()  # most likely in local tz
        activity_tz = self._start.tzinfo

        def to_datetime(local_timestring):
            # Activity file doesn't have microsecond precision so just drop it.
            x = time.fromisoformat(local_timestring)
            return start.replace(
                hour=x.hour, minute=x.minute, second=x.second
            ).astimezone(activity_tz)

        hr = server.fitbit.intraday_time_series(
            "activities/heart",
            base_date=start,
            detail_level="1sec",
            start_time=start,
            end_time=self.end(),
        )["activities-heart-intraday"]["dataset"]

        return [HeartRateSample(to_datetime(x["time"]), x["value"]) for x in hr]

    def create_heart_rate_element(
        self, heart_rate_bpm: int, heart_rate_type: Optional[str] = None
    ) -> minidom.Element:
        """ Create an XML Element Node for a heart rate bpm value. The node must
        be explicitly inserted into the tree.
        """
        xml = self.xml

        e = xml.createElement("Value")
        e.appendChild(xml.createTextNode(str(heart_rate_bpm)))

        if heart_rate_type is None:
            element_name_prefix = ""
        else:
            element_name_prefix = heart_rate_type.title()

        e2 = xml.createElement(f"{element_name_prefix}HeartRateBpm")
        e2.appendChild(e)

        if heart_rate_type is None:
            e2.setAttribute("xsi:type", "HeartRateInBeatsPerMinute_t")

        return e2

    def merge_heart_rate(self, heart_rate_samples: List[HeartRateSample]):
        """ Merge heart rate data into the existing activity. """
        # Methods __eq__ and __lt__ are defined for `HeartRateSample` so that's
        # always on the left side.
        iter_a = iter(heart_rate_samples)
        iter_b = iter(self.times)

        a = next(iter_a)
        b = next(iter_b)
        while True:
            try:
                if a == b:
                    b.parentNode.appendChild(self.create_heart_rate_element(a.bpm))
                    a = next(iter_a)
                    b = next(iter_b)
                elif a < b:
                    a = next(iter_a)
                else:
                    b = next(iter_b)
            except StopIteration:
                break

        # Update max and average heart rate as well.
        max_bpm = max(x.bpm for x in heart_rate_samples)
        max_hr = self.xml.getElementsByTagName("MaximumHeartRateBpm")
        assert len(max_hr) == 1
        max_hr = max_hr[0]
        max_hr.parentNode.replaceChild(
            self.create_heart_rate_element(max_bpm, "Maximum"), max_hr
        )

        avg_bpm = mean(x.bpm for x in heart_rate_samples)
        avg_hr = self.xml.getElementsByTagName("AverageHeartRateBpm")
        assert len(avg_hr) == 1
        avg_hr = avg_hr[0]
        avg_hr.parentNode.replaceChild(
            self.create_heart_rate_element(avg_bpm, "Average"), avg_hr
        )
