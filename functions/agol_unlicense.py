#!/usr/bin/env python
from lazyapi import app
import os
import json, datetime
from arcgis.gis import GIS
from collections import defaultdict
from datetime import datetime

def loadGIS():
    return GIS(username=os.getenv("AGOL_USERNAME"), password=os.getenv("AGOL_PASSWORD"), url=os.getenv("AGOL_URL"))

def content(gis):
    content = defaultdict(list)
    for item in gis.content.search('', max_items=10000):
        content[item.owner].append(item)
    return content

def users(gis):
    users = gis.users.search(max_users=10000)
    mycontent = content(gis)
    userdata = {}
    for user in users:
        userdata[user.username] = {
            "user": user,
            "content": mycontent.get(user.username),
            "daysago": (datetime.now() - datetime.fromtimestamp(user.lastLogin/1000)).days
        }
    return userdata

@app.get("/esri/agol-unlicense")
def agolunlicense():
    gis = loadGIS()
    userdata = users(gis)
    for username, item in userdata.items():
        if not item['content'] and item["daysago"] > 90:
            try: item["user"].delete()
            except Exception as e: print("{}, {}".format(e, username))
            print("may unlicense {}, daysago {}".format(username, item["daysago"]))
    return locals()