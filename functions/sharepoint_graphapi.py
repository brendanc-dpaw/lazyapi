from lazyapi import app
from fastapi import HTTPException
import requests
import os
import json

spgraph_url = os.getenv("SPGRAPH_URL") 
spgraph_spurl = os.getenv("SPGRAPH_SPURL")

@app.get("/spgraph/rename/")
async def spgraph_rename(token: str = "", spsite: str = "", path: str = "", 
                            filename: str = "", tofilename: str = ""):
    if not check_token_valid(token):
        raise HTTPException(status_code=403, detail="Invalid token provided")

    header, expires_in = get_msgraph_token()

    spsite = check_path(spsite)
    path = check_path(path)

    # Get the drive ID
    url = "{}/sites{}{}:/drive".format(spgraph_url, spgraph_spurl, spsite)

    drive_id = requests.get(url, headers=header).json()['id']

    # Get a listing of the drive at the passed in path
    url = "{}/drives/{}/root:{}:/children".format(spgraph_url, drive_id, path)

    dirlist = requests.get(url, headers=header).json()

    # Iterate over the files and find the one we want
    file_id = ""
    for f in dirlist['value']:
        if f['name'] == filename:
            file_id = f['id']

    if file_id == "":
        return "Error file: {} not found".format(filename)

    # Make file access url
    url = "{}/drives/{}/items/{}".format(spgraph_url, drive_id, file_id)

    rename = json.dumps({'name': tofilename})
    
    # Application/json content type required to update driveitem properties.
    header['content-type'] = 'application/json'

    return requests.patch(url, data=rename, headers=header).json()

@app.get("/spgraph/get/")
async def spgraph_get(token: str = "", path: str = ""):
    if not check_token_valid(token):
        raise HTTPException(status_code=403, detail="Invalid token provided")

    header, expires_in = get_msgraph_token()

    url = spgraph_url + path

    return requests.get(url, headers=header).json()

@app.get("/spgraph/delete")
async def spgraph_delete(token: str = "", spsite: str = "", path: str = "", filename: str = ""):
    if not check_token_valid(token):
        raise HTTPException(status_code=403, detail="Invalid token provided")
    
    header, expires_in = get_msgraph_token()

    spsite = check_path(spsite)
    path = check_path(path)

    # Get the drive ID
    url = "{}/sites{}{}:/drive".format(spgraph_url, spgraph_spurl, spsite)

    drive_id = requests.get(url, headers=header).json()['id']

    # Get a listing of the drive at the passed in path
    url = "{}/drives/{}/root:{}:/children".format(spgraph_url, drive_id, path)

    dirlist = requests.get(url, headers=header).json()

    # Iterate over the files and find the one we want
    file_id = ""
    for f in dirlist['value']:
        if f['name'] == filename:
            file_id = f['id']

    if file_id == "":
        raise HTTPEXCEPTION(status_code=404, detail="File: {} not found".format(filename))

    # Make file access url
    url = "{}/drives/{}/items/{}".format(spgraph_url, drive_id, file_id)
    
    return requests.delete(url, headers=header).json()


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


def check_path(path):
    # Ensure there is a preceeding /
    if path[0] != '/':
        path = "/" + path
    # Ensure there is no trailing /
    if path[-1] == '/':
        path = ''.join([path[i] for i in range(len(path)-1)])

    print(path)

    return path
