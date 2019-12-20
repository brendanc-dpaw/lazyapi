from lazyapi import app
from meraki import meraki
from azure.storage.blob import BlobServiceClient
import json, datetime

@app.get("/data-imports/meraki-clients")
def merakiclients():
    APIKEY = os.getenv("MERAKI-API-KEY")
    devices = list()
    clients = list()
    for key in ["meraki-api-key", "blob-connection-string", "meraki-blob-container"]:
        secrets[key] = open("/var/openfaas/secrets/" + key).read().strip()

    mOrgs = meraki.myorgaccess(APIKEY)

    for org in mOrgs:
        for net in meraki.getnetworklist(APIKEY, org["id"]):
            devices += meraki.getnetworkdevices(APIKEY, net["id"])

    for device in devices:
        clients += meraki.getclients(APIKEY, device["serial"])

    blobclient = BlobServiceClient.from_connection_string(os.getenv("BLOB-CONNECTION-STRING"))
    container = blobclient.get_container_client(os.getenv("MERAKI-BLOB-CONTAINER"))
    blobname = "clients-{}.json".format(datetime.date.today().isoformat())
    container.upload_blob(blobname, data=json.dumps(clients, indent=2))

    response = "Uploaded {} containing {} clients".format(blobname, len(clients))
    return response


