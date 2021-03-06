#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime, timedelta
from hashlib import md5

from requests import get

from bs4 import BeautifulSoup, NavigableString
from icalendar import Calendar, Event


def extract_date(entity):
    date = entity.find("div", class_="day").span["content"]
    return datetime.strptime(date[:10], "%Y-%m-%d").date()


def scrape_url(url):
    page = get(url)

    result = []
    for div in BeautifulSoup(page.text, "lxml").find_all(
        "div", class_="view-events-by-day"
    ):
        for row in div.find_all("div", class_="views-row"):
            location = "".join(
                row.find(
                    "div", class_="views-field-field-field-nr-event-location"
                ).stripped_strings
            )
            if "Strasbourg" in location:
                title = row.find("div", class_="views-field-title-field")
                tmp = {
                    "date-start": extract_date(
                        row.find("div", class_="event-date-start")
                    ),
                    "date-end": extract_date(
                        row.find("div", class_="event-date-end")
                    ),
                    "location": location,
                    "title": "".join(title.stripped_strings),
                    "url": title.a["href"],
                }
                result.append(tmp)

    return result


def create_event(d):
    event = Event()
    event.add("summary", d["title"])
    event.add("dtstart", d["date-start"])
    event.add("dtend", d["date-start"] + timedelta(days=4))
    event.add("location", d["location"])
    event.add("uid", "%s@europa.eu" % (md5(d["url"].encode("ascii")).hexdigest(),))
    event.add("description", "https://europa.eu%s" % (d["url"],))

    return event


cal = Calendar()
cal.add("prodid", "-//Calendrier Parlement Européen//europa.eu//")
cal.add("version", "2.0")
cal.add("X-WR-CALNAME", "Calendrier Parlement Européen")

page = 0
url = "https://europa.eu/newsroom/events/year_fr?field_nr_events_by_topic_tid=All&field_nr_event_source_tid=51&field_nr_event_type_tid=All"
while True:
    data = scrape_url(url + "&page=" + repr(page))
    if not data:
        break
    for d in data:
        cal.add_component(create_event(d))
    page +=1

with open("cal_euparl.ics", "w") as f:
    f.write(cal.to_ical().decode("utf-8"))
