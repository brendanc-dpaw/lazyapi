#!/usr/bin/env python
from lazyapi import app
import os
from meraki import meraki
from azure.storage.blob import BlobServiceClient
import json, datetime

@app.get("/data-imports/meraki-clients")
def merakiclients():
    APIKEY = os.getenv("MERAKI_API_KEY")
    devices = list()
    clients = list()

    mOrgs = meraki.myorgaccess(APIKEY)

    for org in mOrgs:
        for net in meraki.getnetworklist(APIKEY, org["id"]):
            devices += meraki.getnetworkdevices(APIKEY, net["id"])

    for device in devices:
        clients += meraki.getclients(APIKEY, device["serial"])

    blobclient = BlobServiceClient.from_connection_string(os.getenv("BLOB_CONNECTION_STRING"))
    container = blobclient.get_container_client(os.getenv("MERAKI_BLOB_CONTAINER"))
    blobname = "clients-{}.json".format(datetime.date.today().isoformat())
    try:
        container.upload_blob(blobname, data=json.dumps(clients, indent=2))
    except Exception as e:
        print(e)

    response = "Uploaded {} containing {} clients".format(blobname, len(clients))
    return response


