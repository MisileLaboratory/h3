from fastapi import FastAPI, Request, status, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from edgedb import create_async_client
from jwt import decode, encode, exceptions

from typing import Annotated
from pathlib import Path
from datetime import timedelta, timezone, datetime
from hashlib import sha3_256

KEY = Path("./KEY").read_text()
TIMEOUT = timedelta(weeks=4) # four weeks
ALG = "HS256"
ORIGINS = ["null", "*"]

app = FastAPI()
app.add_middleware(
  CORSMiddleware,
  allow_origins=ORIGINS,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
)
db = create_async_client()

def utcnow():
  return datetime.now(tz=timezone.utc)

async def check_dupe(userid: str) -> bool:
  return await db.query("select User {id} filter .userid = <str>$userid", userid=userid) != []

@app.get("/check/{userid}")
async def check(request: Request, userid: str) -> bool:
  return await check_dupe(userid)

@app.post("/login")
async def login(
  request: Request,
  userid: Annotated[str | None, Header(alias="id")] = None,
  pw: Annotated[str | None, Header()] = None
) -> str:
  if userid is None or pw is None:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
  if await db.query("select User {id} filter .userid = <str>$userid and .pw = <str>$pw", userid=userid,pw=(sha3_256(pw.encode('utf8'))).hexdigest()) == []:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
  return encode({"exp": utcnow() + TIMEOUT, "id": userid}, KEY, algorithm=ALG)

@app.post("/verify")
async def verify(
  request: Request,
  jwtv: Annotated[str | None, Header(alias="jwt")] = None
):
  if jwtv is None:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
  try:
    j = decode(jwtv, KEY, algorithms=[ALG])
    return j["id"]
  except exceptions.ExpiredSignatureError:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
  except exceptions.DecodeError:
    print('decode')
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

@app.post("/register")
async def register(
  request: Request,
  userid: Annotated[str | None, Header(alias="id")] = None,
  pw: Annotated[str | None, Header()] = None
):
  if userid is None or pw is None:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
  if await check_dupe(userid):
    return HTTPException(status_code=status.HTTP_409_CONFLICT)
  await db.query_single("insert User {userid := <str>$userid, pw := <str>$pw}",userid=userid,pw=sha3_256(pw.encode('utf8')).hexdigest())

