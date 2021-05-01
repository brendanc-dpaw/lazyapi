from lazyapi import app
from fastapi import HTTPException
from pydantic import BaseModel
import requests
import os
import json

class Batch(BaseModel):
    token: str
    path: str
    filename: str
    tofilename: Optional[str] = None

class BatchList(BaseModel):
    batch: List[Batch]


spgraph_url = os.getenv("SPGRAPH_URL") 
spgraph_spurl = os.getenv("SPGRAPH_SPURL")
token_map = {}

@app.get("/spgraph/rename")
async def spgraph_rename(token: str = "", path: str = "", filename: str = "", tofilename: str = ""):
    # Check the token is valid and allowed to access the supplied SP site
    if not check_token_valid(token):
        raise HTTPException(status_code=401)

    # Usage instructions should display if hitting /rename with no params or if any param is missing
    if token == "" or os.getenv("SP_CFG_{}".format(token)) is None or path == "" or filename == "" or tofilename == "":
        return "{'error':'Incorrect URL format','usage':'/spgraph/get/?token=****&path=/path/to/file&filename=myfile&tofilename=newfilename'}"

    # Simple check to make sure paths have correct leading and trailing /
    path = check_path(path)

    header, expires_in = get_msgraph_token()

    dirlist = get_path_children(header, spsite, path)

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

@app.get("/spgraph/get")
async def spgraph_get(token: str = "", path: str = ""):
    # Check the token is valid and allowed to access the supplied SP site
    if not check_token_valid(token):
        raise HTTPException(status_code=401)

    # Usage instructions should display if hitting /get with no params or if any param is missing
    if token == "" or path == "":
        return "{'error':'Incorrect URL format','usage':'/spgraph/get/?token=****&path=/path/to/file'}"

    # Simple check to make sure paths have correct leading and trailing /
    path = check_path(path)

    header, expires_in = get_msgraph_token()

    return get_path_children(header, spsite, path)

@app.get("/spgraph/delete")
async def spgraph_delete(token: str = "", path: str = "", filename: str = ""):
    # Check the token is valid and allowed to access the supplied SP site
    if not check_token_valid(token):
        raise HTTPException(status_code=401)
    
    # Usage instructions should display if hitting /rename with no params or if any param is missing
    if token == "" or path == "" or filename == "":
        return "{'error':'Incorrect URL format','usage':'/spgraph/rename/?token=****&path=/path/to/file&filename=filetodelete'}"
    
    # Simple check to make sure paths have correct leading and trailing /
    path = check_path(path)
   
    header, expires_in = get_msgraph_token()

    dirlist = get_path_children(header, spsite, path)

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

@app.post("/spgraph/batch")
async def spgraph_batch(token: str = "", batch: BatchList):
    # Check the token is valid and allowed to access the supplied SP site
    if not check_token_valid(token):
        raise HTTPException(status_code=401)



    return "Success"

def check_token_valid(request_token):
    # Only load tokens if the token_map is empty
    if not token_map:
        all_tokens = os.getenv("SPGRAPH_VALIDATION_TOKENS")
        tokens = all_tokens.split(";")

        # For each token the should be a corresponding env var that 
        # contains a Sharepoint Site name that it is valid for use with.
        for token in tokens:
            token_map[token] = os.getenv("SPGRAPH_{}".format(token))
        
    if request_token not in token_map.keys():
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

    return path

def get_path_children(header, spsite, path):
    # Get the drive ID
    url = "{}/sites{}{}:/drive".format(spgraph_url, spgraph_spurl, spsite)

    drive_id = requests.get(url, headers=header).json()['id']

    # Get a listing of the drive at the passed in path
    url = "{}/drives/{}/root:{}:/children".format(spgraph_url, drive_id, path)

    return requests.get(url, headers=header).json()
