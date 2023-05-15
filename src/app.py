from genericpath import isdir, isfile
import os
from typing import Optional, List, Union
from pathlib import Path, _ignore_error as pathlib_ignore_error
import shutil

import aiofiles
import aiofiles.os

from fastapi import FastAPI, File, Form, UploadFile, Header, Request, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette.staticfiles import StaticFiles
from starlette.responses import StreamingResponse, RedirectResponse
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

from schemas import InputQuery, OrderByOptions, DirOptions
from users import router, User, get_current_active_user

app = FastAPI(
    title="filesystem_REST",
    description="FastAPI wrapper for filesystem CRUD.",
    version="0.1",
    docs_url=None,
    redoc_url=None
)
app.include_router(router)

@app.get("/retrieve/{localSystemFilePath:path}", tags=['CRUD'],
description="Retrieve")
async def retrieve(localSystemFilePath:str, query: InputQuery = Depends(), 
current_user: User = Depends(get_current_active_user)):
    # check if the path does exist.
    if not os.path.exists(localSystemFilePath):
        raise HTTPException(status_code=404, 
            detail=f"{localSystemFilePath} doesn't exist")
    # if the path is a directory
    if os.path.isdir(localSystemFilePath):
        # get all the result to a list, filter it by name if necessary
        if query.filterByName:
            list_of_files = [f for f in os.listdir(localSystemFilePath) if query.filterByName.lower() in f.lower()]
        elif not query.filterByName:
            list_of_files = [f for f in os.listdir(localSystemFilePath)]
        # set the orderby direction
        asc = True
        if query.orderByDirection == DirOptions.descending:
            asc = False
        # sort the result
        if query.orderBy:
            if query.orderBy == OrderByOptions.fileSize:
                lambda_key = lambda x: os.stat(os.path.join(localSystemFilePath, x)).st_size
            elif query.orderBy == OrderByOptions.fileName:
                lambda_key = lambda x: os.stat(os.path.join(localSystemFilePath, x))
            else:
                lambda_key = lambda x: os.path.getmtime((os.path.join(localSystemFilePath, x)))
            list_of_files = sorted(list_of_files, key = lambda_key, reverse=asc)
        # return the sorted result if there is a match with the query
        if len(list_of_files) > 0:
            resp = {"isDirectory" : True,
                    "folderContent": list(list_of_files)}
            return resp
        # if there is no result after the queries are applied.
        else:
            raise HTTPException(status_code=400, 
                detail=f"No Query Match")
    # if the path is a file
    elif os.path.isfile(localSystemFilePath):
        try:
            # get the file object
            f = open(localSystemFilePath, 'rb')
        except Exception:
            raise HTTPException(status_code=400, detail=f"Error when opening file object")
        # stream it back to the client
        return StreamingResponse(f, media_type='application/octet-stream')

@app.post("/uploadFileStream/{localSystemFilePath:path}", tags=['CRUD'], 
description="Upload a single file; PLEASE DON'T USE THE SWAGGER UI YET for this function")
async def uploadFileStream(localSystemFilePath: str, request: Request, 
current_user: User = Depends(get_current_active_user)):
    # check if need to create folder(s)
    parentDir = os.path.dirname(localSystemFilePath)
    if not os.path.exists(parentDir):
        os.makedirs(parentDir, exist_ok=True)
    # check if there is enough free space for the incoming file
    total, used, free = shutil.disk_usage(parentDir)
    len_input = int(request.headers["filesize"])
    if len_input > free: 
        raise HTTPException(status_code=400, 
            detail=f"file size too big. not enough space.")
    # check if file already exist
    if os.path.exists(localSystemFilePath):
        raise HTTPException(status_code=400, 
            detail=f"{localSystemFilePath} already exist")
    try:
        async with aiofiles.open(localSystemFilePath, 'wb') as f:
            async for chunk in request.stream():
                await f.write(chunk)
            await f.seek(0, os.SEEK_END)
            len_output = await f.tell()
    except Exception:
        raise HTTPException(status_code=400, 
            detail=f"Error when Uploading the File")
    # check if all the file is transferred
    if len_input == len_output:
        return {"message": f"Successfuly uploaded"}
    else:
        raise HTTPException(status_code=400, 
            detail=f"File transfer not complete, len(in) != len(out)")

@app.post("/uploadFile/{localSystemFilePath:path}", tags=['CRUD'], 
description="Upload a single file")
async def uploadFile(localSystemFilePath: str, file: UploadFile = File(...),
current_user: User = Depends(get_current_active_user)):
    # check if need to create folder(s) too
    parentDir = os.path.dirname(localSystemFilePath)
    if not os.path.exists(parentDir):
        os.makedirs(parentDir, exist_ok=True)
    # check if the file already exist
    if os.path.exists(localSystemFilePath):
        raise HTTPException(status_code=404, 
            detail=f"{localSystemFilePath} already exist")
    try:
        # read the file
        contents = await file.read()
        len_input = len(contents)
        # write to disk
        async with aiofiles.open(localSystemFilePath, 'wb') as f:
            await f.write(contents)
            await f.seek(0, os.SEEK_END)
            len_output = await f.tell()
    except Exception:
        raise HTTPException(status_code=400, 
            detail=f"Error when Uploading the File")
    finally:
        await f.close()
    # check if all the file is transferred
    if len_input == len_output:
        return {"message": f"Successfuly uploaded"}
    else:
        raise HTTPException(status_code=400, 
            detail=f"File transfer not complete, len(in) {len_input} != len(out) {len_output}")

@app.patch("/updateFileStream/{localSystemFilePath:path}", status_code=200, tags=['CRUD'], 
description="Update a file; PLEASE DON'T USE THE SWAGGER UI YET for this function")
async def updateFileStream(localSystemFilePath:str, request:Request,
current_user: User = Depends(get_current_active_user)):
    # check if the path exist, if not terminate
    if not os.path.exists(localSystemFilePath):
        raise HTTPException(status_code=404, 
            detail=f"{localSystemFilePath} doesn't exist")
    # check if there is enough free space for the incoming file
    total, used, free = shutil.disk_usage(localSystemFilePath)
    len_input = int(request.headers["filesize"])
    if len_input > free: 
        raise HTTPException(status_code=400, 
            detail=f"file size too big. not enough space.")
    try:
        # stream it in, overwrite the existing file
        async with aiofiles.open(localSystemFilePath, 'wb') as f:
            async for chunk in request.stream():
                await f.write(chunk)
            await f.seek(0, os.SEEK_END)
            len_output = await f.tell()
    except Exception:
        raise HTTPException(status_code=400, 
            detail=f"Error when Updating the File")
    finally:
        await f.close()
    # check if the transfer is really complete
    if len_input == len_output:
        return {"message": f"Successfuly updated"}
    else:
        raise HTTPException(status_code=400, 
            detail=f"File transfer not complete, len(in) {len_input} != len(out) {len_output}")

@app.patch("/updateFile/{localSystemFilePath:path}", status_code=200, tags=['CRUD'], 
description="Update a file")
async def updateFile(localSystemFilePath:str, file: UploadFile = File(...),
current_user: User = Depends(get_current_active_user)):
    # check if the file already exist, if not terminate
    if not os.path.exists(localSystemFilePath):
        raise HTTPException(status_code=404, 
            detail=f"{localSystemFilePath} doesn't exist")
    try:
        contents = await file.read()
        len_input = len(contents)
        async with aiofiles.open(localSystemFilePath, 'wb') as f:
            await f.write(contents)
            await f.seek(0, os.SEEK_END)
            len_output = await f.tell()
    except Exception:
        raise HTTPException(status_code=400, 
            detail=f"Error when Updating the File")
    finally:
        await f.close()
    # check if the file transfer is complete
    if len_input == len_output:
        return {"message": f"Successfuly updated"}
    else:
        raise HTTPException(status_code=400, 
            detail=f"File transfer not complete, len(in) {len_input} != len(out) {len_output}")

@app.delete("/deleteFile/{localSystemFilePath:path}", status_code=200, tags=['CRUD'], 
description="Delete a file")
async def deleteFile(localSystemFilePath:str, current_user: User = Depends(get_current_active_user)):
    # check if the file exist
    if not os.path.exists(localSystemFilePath):
        raise HTTPException(status_code=400, 
            detail=f"{localSystemFilePath} does not exist. Not deleting anything.")
    try:
        os.remove(localSystemFilePath)
    except Exception:
        raise HTTPException(status_code=400, 
            detail=f"Error when Deleting the File")
    # double check if the file still persists.
    if not os.path.exists(localSystemFilePath):
        return {"message": f"Successfuly deleted the File"}
    else:
        raise HTTPException(status_code=400, 
            detail=f"File was not successfully deleted")

@app.get("/ping", status_code=200, tags=['INFO'], description="Check if Alive")
async def ping(current_user: User = Depends(get_current_active_user)):
    return {"ping": "pong"}

@app.get('/', include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url='/static/favicon.png'
    )

@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )