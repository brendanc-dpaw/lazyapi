from lazyapi import app
import requests
import os
import json

spgraph_url = os.getenv("SPGRAPH_URL") 
spgraph_spurl = os.getenv("SPGRAPH_SPURL")

@app.get("/spgraph/rename/")
async def spgraph_rename(token: str = "", spsite: str = "", path: str = "", 
                            filename: str = "", tofilename: str = ""):
    if not check_token_valid(token):
        return "404"

    header, expires_in = get_msgraph_token()

    # Get the drive ID
    url = "{}/sites{}{}:/drive".format(spgraph_url, spgraph_spurl, spsite)

    drive_id = requests.get(url, headers=header).json()['id']

    # Get a listing of the drive at the passed in path
    url = "{}/drives/{}/root:{}/children".format(spgraph_url, drive_id, path)

    dirlist = requests.get(url, headers=header).json()

    file_id = ""
    for f in dirlist['value']:
        if f['name'] == filename:
            file_id = f['id']

    if file_id == "":
        return "Error file: {} not found".format(filename)

    # Make file access url
    url = "{}/drives/{}/items/{}".format(spgraph_url, drive_id, file_id)

    return requests.get(url, headers=header).json()

@app.get("/spgraph/get/")
async def spgraph_get(token: str = "", path: str = ""):
    if not check_token_valid(token):
        return "404"

    header, expires_in = get_msgraph_token()

    url = spgraph_url + path

    return json.loads(requests.get(url, headers=header).text)

@app.get("/spgraph/delete")
async def spgraph_delete():
    if not check_token_valid():
        return "404"
    

    
    response = ""

    return response



def check_token_valid(token):
    print("value: {}  -  {}".format(token, os.getenv("SPGRAPH_VALIDATION_TOKEN")))

    if os.getenv("SPGRAPH_VALIDATION_TOKEN") != token:
        return False

    return True

def get_msgraph_token():
    tenant = os.getenv("SPGRAPH_TENANT_ID")
    client_id = os.getenv("SPGRAPH_CLIENT_ID")
    client_secret = os.getenv("SPGRAPH_CLIENT_SECRET")

    r = requests.post("https://login.microsoftonline.com/{}/oauth2/v2.0/token".format(tenant),
        data={'client_id': client_id, 'client_secret': client_secret, 
            'scope': 'https://graph.microsoft.com/.default',
            'grant_type': 'client_credentials'})

    response = json.loads(r.text)
    
    return ({'Authorization': response['token_type'] + " " + response['access_token']}, response['expires_in']) 
