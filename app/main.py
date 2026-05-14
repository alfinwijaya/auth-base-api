from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.api.routes import auth, user, role, menu, action, role_permission, audit_log
from app.db.base import Base
from app.db.session import engine

app = FastAPI(title="AuthBase API")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"message": "Too many requests"}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(role.router, prefix="/roles", tags=["Roles"])
app.include_router(menu.router, prefix="/menus", tags=["Menus"])
app.include_router(action.router, prefix="/actions", tags=["Actions"])
app.include_router(role_permission.router, prefix="/role-permissions", tags=["Role Permissions"])
app.include_router(audit_log.router, prefix="/audit-logs", tags=["Audit Logs"])