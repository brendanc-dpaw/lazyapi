# lazyapi

[![Build Status](https://dev.azure.com/dbca-wa/ContainerBuilds/_apis/build/status/dbca-wa.lazyapi?branchName=master)](https://dev.azure.com/dbca-wa/ContainerBuilds/_build/latest?definitionId=4&branchName=master)

Simple project based on FastAPI that imports a directory of functions (single python files) and exposes them on port 80

Structure:
- `main.py` - uvicorn entrypoint that imports functions dir and exposes app
- `lazyapi.py` - creates fastapi app and loads dotenv (for local dev)
- `functions/__init__.py` - indexes all functions for import *
- `functions/mycoolfunc.py` - any set of functions/routes

Within a function can just import app and register urls as per [FastAPI Docs](https://fastapi.tiangolo.com/)

``` python
#!/usr/bin/env python
from lazyapi import app
import os

@app.get("/some/neat/url")
def some_func_name():
    APIKEY = os.getenv("SOME_API_KEY")
```

Then you can build it and fire your webhooks!

``` bash
vim .env # fill with secrets
docker build . -t lazyapi # note this image will have your .env in it, don't push it
docker run -d --name lazyapi -p 8000:80 lazyapi
curl localhost:8000/some/neat/url
```
