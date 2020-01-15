#!/usr/bin/env python
from lazyapi import app
import os
import json, datetime
from arcgis.gis import GIS
from collections import defaultdict

def loadGIS():
    return GIS(username=os.getenv("AGOL_USERNAME"), password=os.getenv("AGOL_PASSWORD"), url=os.getenv("AGOL_URL"))

@app.get("/esri/agol-unlicense")
def agolunlicense():
    gis = loadGIS()
    content = defaultdict(list)
    for item in gis.content.search('', max_items=10000):
        content[item.owner].append(item)
    users = gis.users.search()
    for user in users:
        if user.username not in content.keys():
            print("may unlicense {}, lastlogin {}".format(user.username, user.lastLogin))
    return locals()