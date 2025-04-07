from fastapi import FastAPI, HTTPException, Depends,Request
from pydantic import BaseModel, RootModel, Field
from typing import Dict
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm

from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from db_orm.db import get_db
from api_fastapi.db.models import ApiBenchmarkLog,StoredResource
from api_fastapi.db.api_db_handlers import store_json_db, get_stored_json_db
from api_fastapi.db.api_monitor_decorator import benchmark_endpoint
from utils.scriptB import extract_value_from_json
from api_fastapi.app_config import add_bearer_auth_to_openapi
# from api_fastapi.db import api_monitor_decorator

# === Auth Setup ===
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Dummy user
fake_user = {"username": "admin", "password": "admin123"}
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
oauth2_scheme = HTTPBearer()
def authenticate_user(username: str, password: str) -> bool:
    return username == fake_user["username"] and password == fake_user["password"]

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
async def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username != fake_user["username"]:
            raise HTTPException(status_code=401, detail="Invalid user")
        return {"username": username}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username != fake_user["username"]:
            raise HTTPException(status_code=401, detail="Invalid user")
        return {"username": username}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# === FastAPI Setup ===
app = FastAPI(title="JSON Key Reader API",
    description="An authenticated API for storing, processing, and validating JSON data with vectorized operations and benchmarking.",
    version="0.3.0",
    contact={
        "name": "Sagi Levinas",


    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    })

add_bearer_auth_to_openapi(app)

# === Pydantic Models ===
class StoredJson(RootModel):
    root: Dict[str, Dict[str, float]]  # e.g. {"x": {"value": 8}, "y": {"value": -3.2}}


class ValueItem(BaseModel):
    value: float

class MathRequest(BaseModel):
    operation: str = Field(..., examples=["add", "subtract"])
    sources: list[str] = Field(..., example=["A", "B"])

    class Config:
        json_schema_extra = {
            "example": {
                "operation": "add",
                "sources": ["A", "B"]
            }
        }

class VectorMathResponse(RootModel):
    root: Dict[str, ValueItem]

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "x": {"value": 12.0},
                    "y": {"value": 2.0}
                }
            ]
        }

# === Routes API Endpoint===
@app.post(
    "/login",
    summary="Authenticate user and return JWT",
    description="Expects username and password. Returns a JWT token if valid credentials are provided.",
    tags=["Auth"]
)
@benchmark_endpoint("/login")
async def login(
request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),

):
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = create_access_token({"sub": form_data.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}

@app.get(
    "/protected",
    summary="Protected endpoint",
    description="Returns a greeting message for authenticated users. Requires a valid JWT token.",
    tags=["Auth"]
)
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user['username']}! You're authenticated."}

@app.put(
    "/store/{name}",
    summary="Store a named JSON resource",
    description="Stores a JSON object under a given name (e.g., A, B). Requires authentication.",
    tags=["Storage"],  # ✅ Add this line
    responses={
        200: {"description": "JSON stored successfully"},
        401: {"description": "Unauthorized"},
        400: {"description": "Invalid JSON or body"}
    }
)
@benchmark_endpoint("/store")
async def store_json(request: Request,name: str, body: StoredJson, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await store_json_db(name, body.root, db)

@app.get(
    "/store/{name}",
    summary="Retrieve a stored JSON resource Or the value-of resource[key]",
    description="Returns the JSON object stored under the given name (e.g., A, B). Requires authentication.",
    tags=["Storage"],
    responses={
        200: {"description": "Resource returned successfully"},
        401: {"description": "Unauthorized - Invalid or missing token"},
        404: {"description": "Resource not found"}
    }
)
@benchmark_endpoint("/store")
async def get_stored(request: Request,name: str, key: str | None = None, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_stored_json_db(name, key, db)

@app.post(
    "/run_vectorized_math",
    summary="Perform vector math on stored JSONs",
    description="Performs element-wise addition or subtraction on stored JSON objects (A, B, etc.) and returns the result. Requires authentication.",
    tags=["Math Operations"],
    response_model=VectorMathResponse,
    responses={
        200: {"description": "Math operation completed successfully"},
        401: {"description": "Unauthorized - Invalid or missing token"},
        400: {"description": "Bad request or missing resource"}
    }
)
@benchmark_endpoint("run_vectorized_math")
async def run_vector_math_endpoint(request: Request,body: MathRequest, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        result = await run_vector_math_db(body.operation, body.sources, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Math error: {str(e)}")
