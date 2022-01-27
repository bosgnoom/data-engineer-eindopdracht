#!/usr/bin/python

"""
    Uittesten van positie van de zon
"""

import datetime
import pysolar
from zoneinfo import ZoneInfo

# Nauwkeurig genoeg :-)
latitude = 51.2
longitude = 6

# 27-01-2022 12:00
date = datetime.datetime(2022, 1, 27, 12, 00, tzinfo=ZoneInfo('Europe/Amsterdam'))
print(pysolar.solar.get_altitude(latitude, longitude, date))
print(pysolar.solar.get_azimuth(latitude, longitude, date))
print('\n')

# NU
date = datetime.datetime.now(datetime.timezone.utc)
print(pysolar.solar.get_altitude(latitude, longitude, date))
print(pysolar.solar.get_azimuth(latitude, longitude, date))
print('\n')

# Per dag bekijken, altitude = elevation, azimuth = hoek van zon (oost=op=+/- 90, west=weg=+/- 270)
for i in range(7, 24):
    date = datetime.datetime(2022, 3, 31, i, 00, tzinfo=ZoneInfo('Europe/Amsterdam'))
    print(i, pysolar.solar.get_altitude(latitude, longitude, date), pysolar.solar.get_azimuth(latitude, longitude, date))
