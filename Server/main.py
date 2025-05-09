# https://github.com/hogeline/sample_fastapi
from datetime import datetime, date

import uvicorn
from fastapi import FastAPI, File, UploadFile, Depends, Header, HTTPException
from typing import List

from sqlalchemy import TIMESTAMP, and_
from sqlalchemy.orm import Session
from starlette import status
from starlette.background import BackgroundTasks
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

from config import config
from recipe import recipe
from server import server
from result import result
from machinemodel import machinemodel
from logfile import logfile




app = FastAPI(
    title="SYSTEM CONFIG",
    description="EDIT CONFIC SYSTEM BELOW",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(result.result,
                    tags=["Result"],
                    responses={200: {"message": "OK"}}
                    )

app.include_router(config.config,
                   tags=["Config"],
                   responses={200: {"message": "OK"}}
                   )

#app.include_router(lastrecipe.lastrecipe,
#                   prefix="/lastrecipe",
#                   tags=["Last_recipe"],
#                   responses={200: {"message": "OK"}}
#                   )

app.include_router(recipe.recipe,
                   tags=["Recipe"],
                   responses={200: {"message": "OK"}}
                   )

#app.include_router(server.server,
#                   #prefix="/server",
#                   tags=["Server"],
#                   responses={200: {"message": "OK"}}
#                   )

app.include_router(machinemodel.Machinemodel,
                    tags=["MacineModel"],
                    responses={200: {"message": "OK"}}
                    # )

app.include_router(logfile.log_info,
                    tags=["LOG"],
                    responses={200: {"message": "OK"}}
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="info")
