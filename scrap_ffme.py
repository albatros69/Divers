#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime
from os import environ

from requests import get

from bs4 import BeautifulSoup, NavigableString
from icalendar import Calendar, Event

# Pour faire du TLS1.0...
environ["OPENSSL_CONF"] = "openssl.cnf"

def scrape_url(url):
    page = get(url)

    result = [ ]
    for div in BeautifulSoup(page.text, 'lxml').find_all('div', class_='infos_colonne_box'):
        rows = div.find_all('tr')
        if rows:
            headers = [ ' '.join(x.stripped_strings) for x in rows[0] if not isinstance(x, NavigableString) ]
            for row in rows[1:]:
                result.append(
                    dict(zip(headers, [ x for x in row if not isinstance(x, NavigableString) ]))
                )

    return result


def create_event_formation(d):
    event = Event()
    dates = tuple(d['Date'].stripped_strings)
    num = ''.join(d['N°'].stripped_strings)
    event.add('summary',     ' '.join(d['Nom'].stripped_strings))
    event.add('dtstart',     datetime.strptime(dates[0], '%d/%m/%y').date())
    if len(dates) > 1:
        event.add('dtend',   datetime.strptime(dates[1], '%d/%m/%y').date())
    event.add('location',    ' '.join(d['Lieu'].stripped_strings).replace("\r\n", ' '))
    event.add('uid', "%s@formation.ffme.fr" % (num,) )
    event.add('description', 'http://www.ffme.fr/formation/fiche-evenement/%s.html' % (num, ))

    return event


def create_event_compet(d):
    event = Event()
    nom_lieu = tuple(d['Nom de la compétition Lieu'].stripped_strings)
    dates = tuple(d['Date'].stripped_strings)
    link = 'http://www.ffme.fr'+d['Nom de la compétition Lieu'].a.get('href')
    event.add('summary',     nom_lieu[0])
    event.add('location',    nom_lieu[1])
    event.add('dtstart',     datetime.strptime(dates[0], '%d/%m/%y').date())
    if len(dates) > 1:
        event.add('dtend',   datetime.strptime(dates[1], '%d/%m/%y').date())
    event.add('uid', "%s@competition.ffme.fr" % (''.join(( a for a in link if a.isdigit())),) )
    event.add('description', link)

    return event


cal = Calendar()
cal.add('prodid', '-//Calendrier formations FFME//ffme.fr//')
cal.add('version', '2.0')
cal.add("X-WR-CALNAME", "Calendrier formations FFME")

urls = ('http://www.ffme.fr/formation/calendrier-liste/FMT_ESCSAE.html',
        'http://www.ffme.fr/formation/calendrier-liste/FMT_ESCSNE.html',
        #'http://www.ffme.fr/formation/calendrier-liste/FMT_ESCFCINI.html',
        'http://www.ffme.fr/formation/calendrier-liste/FMT_ESCMONESP.html',
)

for u in urls:
    for d in scrape_url(u):
        cal.add_component(create_event_formation(d))

with open('cal_formation.ics', 'w') as f:
   f.write(cal.to_ical().decode('utf-8'))

cal = Calendar()
cal.add('prodid', '-//Calendrier compétitions FFME//ffme.fr//')
cal.add('version', '2.0')
cal.add("X-WR-CALNAME", "Calendrier compétitions FFME")

url = 'http://www.ffme.fr/competition/calendrier-liste.html?DISCIPLINE=ESC&CPT_FUTUR=1'

page = 1
while True:
    data = scrape_url(url + "&page=" + repr(page))
    if not data:
        break
    for d in data:
        cal.add_component(create_event_compet(d))
    page +=1

with open('cal_competition.ics', 'w') as f:
   f.write(cal.to_ical().decode('utf-8'))
