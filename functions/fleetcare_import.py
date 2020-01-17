#!/usr/bin/env python
from lazyapi import app
import os
from peewee import PostgresqlDatabase, Model, CharField, DateTimeField, TextField
from collections import defaultdict
import json

db = PostgresqlDatabase(os.environ["PGDATABASE"])

class LogEntry(Model):
    name = CharField()
    created = DateTimeField()
    text = TextField()

    class Meta:
        indexes = (
            (('name', 'created'), True),
        )
        database = db

def init_database():
    db.connect()
    db.create_tables([LogEntry])

def getEntryList():
    entries = defaultdict(list)
    for entry in LogEntry.select():
        filename = entry.name
        try:
            data = json.loads(entry.text)
            deviceid = data["vehicleID"]
        except Exception as e:
            print(e)
            continue
        entries[deviceid].append({"filename": filename, "data": data})
    return entries


