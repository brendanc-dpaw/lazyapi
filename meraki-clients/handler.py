from meraki import meraki
from azure.storage.blob import BlobServiceClient
import json

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    secrets = dict()
    devices = list()
    clients = list()
    for key in ["meraki-api-key", "blob-connection-string", "meraki-blob-container"]:
        secrets[key] = open("/var/openfaas/secrets/" + key).read().strip()

    mOrgs = meraki.myorgaccess(secrets["meraki-api-key"])

    for org in mOrgs:
        for net in meraki.getnetworklist(secrets["meraki-api-key"], org["id"]):
            devices += meraki.getnetworkdevices(secrets["meraki-api-key"], net["id"])

    for device in devices:
        clients += meraki.getclients(secrets["meraki-api-key"], device["serial"])

    blobclient = BlobServiceClient.from_connection_string(secrets["blob-connection-string"])
    container = blobclient.get_container_client(secrets["meraki-blob-container"])
    blobname = "clients-{}.json".format(datetime.date.today().isoformat())
    container.upload_blob(blobname, data=json.dumps(clients, indent=2))

    response = "Uploaded {} containing {} clients".format(blobname, len(clients))
    return response


