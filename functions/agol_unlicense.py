#!/usr/bin/env python
from lazyapi import app
import os
import json, datetime
from arcgis.gis import GIS

@app.get("/esri/agol-unlicense")
def agolunlicense():
    gis = GIS(username=os.getenv("AGOL_USERNAME"), password=os.getenv("AGOL_PASSWORD"), url=os.getenv("AGOL_URL"))
    return gis
