from httpx import post
from edgedb import create_async_client
from fastapi import FastAPI, Header, HTTPException, Request, status, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from os import listdir, getcwd
from os.path import getsize, isfile, join, realpath, abspath, isdir
from typing import Annotated

#SCHALE_URL = "https://schale.misile.xyz"
SCHALE_URL = "http://localhost:10001"
ROOT_PATH = join(getcwd(), "files")
ORIGINS = ["*"]

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.add_middleware(
 CORSMiddleware,
 allow_origins=ORIGINS,
 allow_credentials=True,
 allow_methods=["*"],
 allow_headers=["*"]
)
app.mount("/file", StaticFiles(directory="files"), "files")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

db = create_async_client()

def is_safe_path(path, follow_symlinks=True):
  if follow_symlinks:
    return realpath(path).startswith(ROOT_PATH)
  else:
    return abspath(path).startswith(ROOT_PATH)

@app.get("/")
@limiter.limit("1/second")
async def get_gpg(request: Request, jwtv: Annotated[str, Header(alias="jwt")] = ""):
 r = post(f"{SCHALE_URL}/verify", headers={'jwt':jwtv})
 if not r.is_success:
  raise HTTPException(status_code=r.status_code)
 return await db.query_json("select User {groups} filter .userid = <str>$userid", userid=r.text)

@app.get("/files")
@limiter.limit("10/second")
async def get_files(request: Request, path: Annotated[str, Header()] = "."):
 if not is_safe_path(join(ROOT_PATH, path)):
  raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
 if not isdir(join(ROOT_PATH, path)):
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
 return [{"name": x, "size": getsize(join(ROOT_PATH, path, x)), "dir": isdir(join(ROOT_PATH, path, x))} for x in listdir(f'{ROOT_PATH}/{path}')]

@app.post("/uploadfile")
@limiter.limit("10/minute")
async def upload_file(request: Request, file: UploadFile, jwtv: Annotated[str, Header(alias="jwt")] = "", path: Annotated[str | None, Header()] = None):
 if not is_safe_path(join(ROOT_PATH, path)):
  raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
 r = post(f"{SCHALE_URL}/verify", headers={'jwt':jwtv})
 if not r.is_success:
  raise HTTPException(status_code=r.status_code)
 if not await db.query_single("select User {admin} filter .userid = <str>$userid", userid=r.text):
  raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
 if isfile(f"{ROOT_PATH}/{path}/{file.filename}"):
  raise HTTPException(status_code=status.HTTP_409_CONFLICT)
 with open(f"{ROOT_PATH}/{path}/{filename}", "wb") as f:
  f.write(file.file)

