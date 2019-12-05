from meraki import meraki
import json

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    apikey = open("/var/openfaas/secrets/meraki-api-key").read().strip()

    mOrgs = meraki.myorgaccess(apikey)
    devices = list()
    clients = list()

    for org in mOrgs:
        for net in meraki.getnetworklist(apikey, org["id"]):
            devices += meraki.getnetworkdevices(apikey, net["id"])

    for device in devices:
        clients += meraki.getclients(apikey, device["serial"])

    return json.dumps(clients)


